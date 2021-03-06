#!/usr/bin/python -B

from string       import Template, upper, replace
from ApiUtil      import outputCode
from ApiUtil      import typeIsVoid
from ApiUtil      import toLong
from ApiUtil      import hexValue
from ApiCodeGen   import *
from Emu          import emuFindEntry, emuCodeGen

from RegalContext     import emuRegal
from RegalContextInfo import cond
from RegalSystem      import regalSys

publicHeaderTemplate = Template( '''${AUTOGENERATED}
${LICENSE}

#ifndef __REGAL_DECLARATIONS_H
#define __REGAL_DECLARATIONS_H

${REGAL_SYS}

#if REGAL_SYS_WGL
# define REGAL_CALL __stdcall
#else
# define REGAL_CALL
#endif

#ifndef GLAPIENTRY
#define GLAPIENTRY REGAL_CALL
#endif

#ifdef _WIN32
#  if REGAL_DECL_EXPORT
#    define REGAL_DECL
#  else
#    define REGAL_DECL __declspec(dllimport)
#  endif
#elif defined(__GNUC__) && __GNUC__>=4
#  if REGAL_DECL_EXPORT
#    define REGAL_DECL __attribute__ ((visibility("default")))
#  else
#    define REGAL_DECL
#  endif
#elif defined(__SUNPRO_C) || defined(__SUNPRO_CC)
#  if REGAL_DECL_EXPORT
#    define REGAL_DECL __global
#  else
#    define REGAL_DECL
#  endif
#else
#  define REGAL_DECL
#endif

#endif /* __REGAL_DECLARATIONS_H */

#ifndef __${HEADER_NAME}_H__
#define __${HEADER_NAME}_H__

/* Skip OpenGL API if another header was included first. */

#if !defined(__gl_h_) && !defined(__GL_H__) && !defined(__X_GL_H) && !defined(__gl2_h_) && !defined(__glext_h_) && !defined(__GLEXT_H_) && !defined(__gl_ATI_h_) && !defined(_OPENGL_H)

#define __gl_h_
#define __gl2_h_
#define __GL_H__
#define __X_GL_H
#define __glext_h_
#define __GLEXT_H_
#define __gl_ATI_h_
#define _OPENGL_H

#if REGAL_SYS_GLX
#include <X11/Xdefs.h>
#include <X11/Xutil.h>
typedef XID GLXDrawable;
#endif

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>
#if REGAL_SYS_WGL
  typedef __int64 int64_t;
  typedef unsigned __int64 uint64_t;
  #ifdef  REGAL_SYS_WGL_DECLARE_WGL
    #ifndef _WINDEF_
      struct HDC__ {int unused;};
      typedef struct HDC__* HDC;
      struct HGLRC__ {int unused;};
      typedef struct HGLRC__* HGLRC;
    #endif
  #endif
#else
# include <inttypes.h>
#endif

${API_TYPEDEF}

/* TODO: make this automatic? */

typedef void (*GLDEBUGPROCAMD)(GLuint id, GLenum category, GLenum severity, GLsizei length, const GLchar *message, GLvoid *userParam);
typedef void (*GLDEBUGPROCARB)(GLenum source, GLenum type, GLuint id, GLenum severity, GLsizei length, const GLchar *message, GLvoid *userParam);
typedef void (*GLDEBUGPROC)(GLenum source, GLenum type, GLuint id, GLenum severity, GLsizei length, const GLchar *message, GLvoid *userParam);

typedef void (*GLLOGPROCREGAL)(GLenum stream, GLsizei length, const GLchar *message, GLvoid *context);

${API_ENUM}

${API_FUNC_DECLARE}

#ifdef __cplusplus
}
#endif

#endif /* __gl_h_ etc */
#endif /* __REGAL_H__ */

#ifndef __REGAL_API_H
#define __REGAL_API_H

#if REGAL_SYS_NACL
#include <stdint.h>
struct PPB_OpenGLES2;
#endif

/* Regal-specific API... try to keep this minimal
   this is a seperate include guard to work nicely with RegalGLEW.h
*/

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*RegalErrorCallback)(GLenum);
REGAL_DECL RegalErrorCallback RegalSetErrorCallback( RegalErrorCallback callback );

#if REGAL_SYS_NACL
typedef int32_t RegalSystemContext;
REGAL_DECL void RegalMakeCurrent( RegalSystemContext ctx, struct PPB_OpenGLES2 *interface );
#else
typedef void * RegalSystemContext;
REGAL_DECL void RegalMakeCurrent( RegalSystemContext ctx );
#endif

#ifdef __cplusplus
}
#endif

#endif /* __REGAL_API_H */
''')

def generatePublicHeader(apis, args):

  apiTypedef     = apiTypedefCode( apis, args )
  apiEnum        = apiEnumCode(apis, args)                 # CodeGen for API enums
  apiFuncDeclare = apiFuncDeclareCode( apis, args )        # CodeGen for API functions

  # Output

  substitute = {}
  substitute['LICENSE']       = args.license
  substitute['AUTOGENERATED'] = args.generated
  substitute['COPYRIGHT']     = args.copyright
  substitute['HEADER_NAME']   = "REGAL"
  substitute['REGAL_SYS']     = regalSys
  substitute['API_TYPEDEF']      = apiTypedef
  substitute['API_ENUM']         = apiEnum
  substitute['API_FUNC_DECLARE'] = apiFuncDeclare

  outputCode( 'include/GL/Regal.h', publicHeaderTemplate.substitute(substitute))

## Map gl.py helper functions to Regal namespace

helpers = {
  'helperGLCallListsSize'         : 'helper::size::callLists',
  'helperGLFogvSize'              : 'helper::size::fogv',
  'helperGLLightvSize'            : 'helper::size::lightv',
  'helperGLLightModelvSize'       : 'helper::size::lightModelv',
  'helperGLMaterialvSize'         : 'helper::size::materialv',
  'helperGLTexParametervSize'     : 'helper::size::texParameterv',
  'helperGLTexEnvvSize'           : 'helper::size::texEnvv',
  'helperGLTexGenvSize'           : 'helper::size::texGenv',
  'helperGLNamedStringSize'       : 'helper::size::namedString',
#  'helperGLDrawElementsSize'      : 'helper::size::drawElements',
  'helperGLNamedStringParamsSize' : 'helper::size::namedStringParams'
}

def apiFuncDefineCode(apis, args):

  code = ''
  for api in apis:

    tmp = []
    for function in api.functions:

      name       = function.name
      params     = paramsDefaultCode(function.parameters, True)
      callParams = paramsNameCode(function.parameters)
      rType      = typeCode(function.ret.type)
      category   = getattr(function, 'category', None)
      version    = getattr(function, 'version', None)

      if category:
        category = category.replace('_DEPRECATED', '')
      elif version:
        category = version.replace('.', '_')
        category = 'GL_VERSION_' + category

      c = ''
      c += 'REGAL_DECL %sREGAL_CALL %s(%s) \n{\n' % (rType, name, params)

      emue = [ emuFindEntry( function, i['formulae'], i['member'] ) for i in emuRegal ]

      if function.needsContext:
        c += '  RegalContext *_context = GET_REGAL_CONTEXT();\n'
        c += '  %s\n' % debugPrintFunction( function, 'App' )
        c += '  if (!_context) return'
        if typeIsVoid(rType):
          c += ';\n'
        else:
          if rType[-1] != '*':
            c += ' (%s)0;\n' % ( rType )
          else:
            c += ' NULL;\n'

        c += listToString(indent(emuCodeGen(emue,'impl'),'  '))

        if getattr(function,'regalRemap',None)!=None and (isinstance(function.regalRemap, list) or isinstance(function.regalRemap, str) or isinstance(function.regalRemap, unicode)):
          c += '  '
          if not typeIsVoid(rType):
            c += 'return '
          if isinstance(function.regalRemap, list):
            c += '\n  '.join(function.regalRemap) + '\n'
          else:
            c += '%s;\n'%(function.regalRemap)
        else:
          if getattr(function,'regalOnly',False)==False:
            c += '  DispatchTable *_next = &_context->dispatcher.front();\n'
            c += '  RegalAssert(_next);\n'
            c += '  '
            if not typeIsVoid(rType):
              c += 'return '
            c += '_next->call(&_next->%s)(%s);\n' % ( name, callParams )
      else:
        c += '  %s\n' % debugPrintFunction(function, 'App' )

        if api.name=='egl':
          c += '\n'
          c += '  #if !REGAL_STATIC_EGL\n'

        c += '  if (dispatchTableGlobal.%s == NULL) {\n' % name
        c += '    GetProcAddress( dispatchTableGlobal.%s, "%s" );\n' % ( name, name )
        c += '    RegalAssert(dispatchTableGlobal.%s!=%s);\n' % ( name, name )
        c += '    if (dispatchTableGlobal.%s==%s)\n' % ( name, name )
        c += '      dispatchTableGlobal.%s = NULL;\n' % ( name )
        c += '  }\n'

        if api.name=='egl':
          c += '  #endif // !REGAL_STATIC_EGL\n\n'

        if not typeIsVoid(rType):
          if rType[-1] != '*':
            c += '  %s ret = (%s)0;\n' % ( rType, rType )
          else:
            c += '  %s ret = NULL;\n' % rType

        c += listToString(indent(emuCodeGen(emue,'impl'),'  '))

        c += '  if (dispatchTableGlobal.%s) {\n' % name
        c += '    %s\n' % debugPrintFunction( function, 'Driver' )
        c += '    '
        if not typeIsVoid(rType):
          c += 'ret = '
        c += 'dispatchTableGlobal.%s(%s);\n' % ( name, callParams )
        if name == 'wglMakeCurrent':
          c += '    RegalMakeCurrent(RegalSystemContext(hglrc));\n'
        elif name == 'CGLSetCurrentContext':
          c += '    RegalMakeCurrent( ctx );\n'
        elif name == 'glXMakeCurrent':
          c += '    RegalMakeCurrent( RegalSystemContext(ctx) );\n'
        elif name == 'eglMakeCurrent':
          c += '    RegalMakeCurrent( ctx );\n'
        c += '  }\n'
        c += '  else\n'
        c += '    Warning( "%s not available." );\n' % name

        c += listToString(indent(emuCodeGen(emue,'suffix'),'  '))

        if not typeIsVoid(rType):
          c += '  return ret;\n'
      c += '}\n\n'

      tmp.append( (category, c) )

    tmp = listToString(unfoldCategory(tmp))

    if api.name in cond:
      tmp = wrapIf(cond[api.name], tmp)

    code += tmp

  return code

# debug print function
def debugPrintFunction(function, trace = 'ITrace'):
  c =  ''
  args = []
  for i in function.parameters:

    if i.output:
      continue

    # Use a cast, if necessary

    t = i.type
    n = i.name
    if i.cast != None:
      t = i.cast
      n = 'reinterpret_cast<%s>(%s)'%(t,n)

    # If it's array of strings, quote each string

    quote = ''
    if t == 'char **' or t == 'const char **' or t == 'GLchar **' or t == 'const GLchar **' or t == 'LPCSTR *':
      quote = ',"\\\""'

    if i.regalLog != None:
      args.append('%s'%i.regalLog)
    elif t == 'GLenum':
      args.append('toString(%s)'%n)
    elif t == 'GLboolean' or t == 'const GLboolean':
      args.append('toString(%s)'%n)
    elif t == 'char *' or t == 'const char *' or t == 'GLchar *' or t == 'const GLchar *' or t == 'LPCSTR':
      args.append('boost::print::quote(%s,\'"\')'%n)
    elif i.input and i.size!=None and (isinstance(i.size,int) or isinstance(i.size, long)) and t.find('void')==-1 and t.find('PIXELFORMATDESCRIPTOR')==-1:
      args.append('boost::print::array(%s,%s)'%(n,i.size))
    elif i.input and i.size!=None and (isinstance(i.size, str) or isinstance(i.size, unicode)) and t.find('void')==-1 and t.find('PIXELFORMATDESCRIPTOR')==-1 and i.size.find('helper')==-1:
      args.append('boost::print::array(%s,%s%s)'%(n,i.size,quote))
    elif i.input and i.size!=None and (isinstance(i.size, str) or isinstance(i.size, unicode)) and t.find('void')==-1 and t.find('PIXELFORMATDESCRIPTOR')==-1 and i.size.find('helper')==0:
      h = i.size.split('(')[0]
      if h in helpers:
        args.append('boost::print::array(%s,%s(%s%s)'%(n,helpers[h],i.size.split('(',1)[1],quote))
      else:
        args.append(n)
    elif t.startswith('GLDEBUG'):
      pass
    elif t.startswith('GLLOGPROC'):
      pass
    else:
      args.append(n)

  args = args[:9]
  if len(args):
    c += '%s("%s","(", ' % (trace, function.name)
    c += ', ", ", '.join(args)
    c += ', ")");'
  else:
    c += '%s("%s","()");' % (trace, function.name)
  return c

def apiTypedefCode( apis, args ):

  code = ''
  for api in apis:
    code += '\n'
    if api.name in cond:
      code += '#if %s\n' % cond[api.name]
    if api.name == 'wgl':
      code += '#ifdef  REGAL_SYS_WGL_DECLARE_WGL\n'
      code += '#ifndef _WINDEF_\n'
    for typedef in api.typedefs:

      if api.name == 'wgl' and typedef.name=='GLYPHMETRICSFLOAT':
        code += '#endif\n'
        code += '#ifndef _WINGDI_\n'
      if api.name == 'wgl' and typedef.name=='HPBUFFERARB':
        code += '#endif\n'

      if re.search( '\(\s*\*\s*\)', typedef.type ):
        code += 'typedef %s;\n' % ( re.sub( '\(\s*\*\s*\)', '(*%s)' % typedef.name, typedef.type ) )
      else:
        code += 'typedef %s %s;\n' % ( typedef.type, typedef.name )

    if api.name == 'wgl':
      code += '#endif // REGAL_SYS_WGL_DECLARE_WGL\n'
    if api.name in cond:
      code += '#endif // %s\n' % cond[api.name]
    code += '\n'

  return code

# CodeGen for custom API definitions.

def apiEnumCode( apis, args ):

  code = ''
  for api in apis:
    code += '\n'
    if api.name in cond:
      code += '#if %s\n' % cond[api.name]
    if api.name == 'wgl':
      code += '#if REGAL_SYS_WGL_DECLARE_WGL\n'
    for enum in api.enums:
      if enum.name == 'defines':
        pass
      else:
        code += '\ntypedef enum _%s {\n' % enum.name
        for enumerant in enum.enumerants:
          code += '  %s = %s,\n' % ( enumerant.name, enumerant.value )
        code += '} %s;\n\n' % enum.name
    if api.name == 'wgl':
      code += '#endif // REGAL_SYS_WGL_DECLARE_WGL\n'
    if api.name in cond:
      code += '#endif // %s\n' % cond[api.name]
    code += '\n'

  return code

# CodeGen for API function declaration.

def apiFuncDeclareCode(apis, args):
  code = ''

  for api in apis:

    d = [] # defines
    e = [] # enums
    t = [] # function pointer typedefs
    m = [] # mangled names for REGAL_NAMESPACE support
    f = [] # gl names

    for enum in api.enums:
      if enum.name == 'defines':
        for enumerant in enum.enumerants:
          value = toLong(enumerant.value)
          if value==None:
            value = enumerant.value

          # Don't bother with decimal for 0-10
          if isinstance(value, long) and value>=10:
            e.append((enumerant.category, '#define %s %s /* %s */'%(enumerant.name,hexValue(value),value)))
          else:
            e.append((enumerant.category, '#define %s %s'%(enumerant.name,hexValue(value))))

    for function in api.functions:

      name   = function.name
      params = paramsDefaultCode(function.parameters, True)
      rType  = typeCode(function.ret.type)
      category  = getattr(function, 'category', None)
      version   = getattr(function, 'version', None)

      if category:
        category = category.replace('_DEPRECATED', '')
      elif version:
        category = version.replace('.', '_')
        category = 'GL_VERSION_' + category

      t.append((category,funcProtoCode(function, version, 'REGAL_CALL', True)))
      m.append((category,'#define %-35s r%-35s' % (name, name) ))
      f.append((category,'REGAL_DECL %sREGAL_CALL %s(%s);' % (rType, name, params) ))

    def cmpEnum(a,b):
      if a[0]==b[0]:
        aValue = a[1].split(' ')[2]
        bValue = b[1].split(' ')[2]
        if aValue==bValue:
          return cmp(a[1].split(' ')[1], b[1].split(' ')[1])
        else:
          return cmp(aValue,bValue)
      return cmp(a[0],b[0])

    def enumIfDef(category):
      return '#ifndef REGAL_NO_ENUM_%s'%(upper(category).replace(' ','_'))

    def typedefIfDef(category):
      return '#ifndef REGAL_NO_TYPEDEF_%s'%(upper(category).replace(' ','_'))

    def namespaceIfDef(category):
      return '#ifndef REGAL_NO_NAMESPACE_%s'%(upper(category).replace(' ','_'))

    def declarationIfDef(category):
      return '#ifndef REGAL_NO_DECLARATION_%s'%(upper(category).replace(' ','_'))

    categories = set()
    categories.update([ i[0] for i in e ])
    categories.update([ i[0] for i in t ])
    categories.update([ i[0] for i in m ])
    categories.update([ i[0] for i in f ])

    for i in categories:
      if len(i):
        cat = upper(i).replace(' ','_')

        d.append((i,'#if (defined(%s) || defined(REGAL_NO_ENUM) || defined(REGAL_NO_%s)) && !defined(REGAL_NO_ENUM_%s)'%(cat,cat,cat)))
        d.append((i,'#define REGAL_NO_ENUM_%s'%(cat)))
        d.append((i,'#endif'))
        d.append((i,''))

        d.append((i,'#if (defined(%s) || defined(REGAL_NO_TYPEDEF) || defined(REGAL_NO_%s)) && !defined(REGAL_NO_TYPEDEF_%s)'%(cat,cat,cat)))
        d.append((i,'#define REGAL_NO_TYPEDEF_%s'%(cat)))
        d.append((i,'#endif'))
        d.append((i,''))

        d.append((i,'#if (defined(%s) || !defined(REGAL_NAMESPACE) || defined(REGAL_NO_%s)) && !defined(REGAL_NO_NAMESPACE_%s)'%(cat,cat,cat)))
        d.append((i,'#define REGAL_NO_NAMESPACE_%s'%(cat)))
        d.append((i,'#endif'))
        d.append((i,''))

        d.append((i,'#if (defined(%s) || defined(REGAL_NO_DECLARATION) || defined(REGAL_NO_%s)) && !defined(REGAL_NO_DECLARATION_%s)'%(cat,cat,cat)))
        d.append((i,'#define REGAL_NO_DECLARATION_%s'%(cat)))
        d.append((i,'#endif'))
        d.append((i,''))

        d.append((i,'#ifndef %s'%(i)))
        d.append((i,'#define %s 1'%(i)))
        d.append((i,'#endif'))
        d.append((i,''))

    e.sort(cmpEnum)
    e = alignDefineCategory(e)
    e = ifCategory(e,enumIfDef)
    e = spaceCategory(e)

    t.sort()
    t = ifCategory(t,typedefIfDef)
    t = spaceCategory(t)

    m.sort()
    m = ifCategory(m,namespaceIfDef)
    m = spaceCategory(m)

    f.sort()
    f = ifCategory(f,declarationIfDef)
    f = spaceCategory(f)

    d.extend(e)
    d.extend(t)
    d.extend(m)
    d.extend(f)

    tmp = listToString(unfoldCategory(d,'/**\n ** %s\n **/',lambda x,y: cmp(x[0], y[0])))

    if api.name == 'wgl':
      tmp = wrapIf('REGAL_SYS_WGL_DECLARE_WGL',tmp)
    if api.name in cond:
      tmp = wrapIf(cond[api.name], tmp)

    code += '%s\n'%(tmp)

  return code

# CodeGen for dispatch table init.

def apiGlobalDispatchFuncInitCode(apis, args):
  categoryPrev = None
  code = ''

  for api in apis:

    code += '\n'
    if api.name in cond:
      code += '#if %s\n' % cond[api.name]

    for function in api.functions:
      if function.needsContext:
        continue

      name   = function.name
      params = paramsDefaultCode(function.parameters, True)
      callParams = paramsNameCode(function.parameters)
      rType  = typeCode(function.ret.type)
      category  = getattr(function, 'category', None)
      version   = getattr(function, 'version', None)

      if category:
        category = category.replace('_DEPRECATED', '')
      elif version:
        category = version.replace('.', '_')
        category = 'GL_VERSION_' + category

      # Close prev category block.
      if categoryPrev and not (category == categoryPrev):
        code += '\n'

      # Begin new category block.
      if category and not (category == categoryPrev):
        code += '// %s\n\n' % category

      categoryPrev = category

      code += '  dispatchTableGlobal.%s = %s_%s;\n' % ( name, 'loader', name )

    if api.name in cond:
      code += '#endif // %s\n' % cond[api.name]
    code += '\n'

  # Close pending if block.
  if categoryPrev:
    code += '\n'

  return code

sourceTemplate = Template('''${AUTOGENERATED}
${LICENSE}

#include "pch.h" /* For MS precompiled header support */

#include "RegalUtil.h"

REGAL_GLOBAL_BEGIN

#include "RegalLog.h"
#include "RegalIff.h"
#include "RegalPush.h"
#include "RegalToken.h"
#include "RegalState.h"
#include "RegalHelper.h"
#include "RegalPrivate.h"
#include "RegalDebugInfo.h"
#include "RegalContextInfo.h"

#include "RegalMarker.h"

using namespace REGAL_NAMESPACE_INTERNAL;
using namespace ::REGAL_NAMESPACE_INTERNAL::Logging;
using namespace ::REGAL_NAMESPACE_INTERNAL::Token;

#ifdef __cplusplus
extern "C" {
#endif

${API_FUNC_DEFINE}

#ifdef __cplusplus
}
#endif

REGAL_GLOBAL_END
''')

def generateSource(apis, args):

  # CodeGen for API functions.

  apiFuncDefine = apiFuncDefineCode( apis, args )
  globalDispatch = apiGlobalDispatchFuncInitCode( apis, args )

  # Output

  substitute = {}
  substitute['LICENSE']         = args.license
  substitute['AUTOGENERATED']   = args.generated
  substitute['COPYRIGHT']       = args.copyright
  substitute['API_FUNC_DEFINE'] = apiFuncDefine
  substitute['API_GLOBAL_DISPATCH_INIT'] = globalDispatch

  outputCode( '%s/Regal.cpp' % args.outdir, sourceTemplate.substitute(substitute))

##############################################################################################

def generateDefFile(apis, args, additional_exports):

  code1 = []
  code2 = []
  code3 = []

  for i in apis:
    if i.name=='wgl' or i.name=='gl':
      for j in i.functions:
        code1.append('  %s'%j.name)
        code2.append('  r%s'%j.name)
    if i.name=='cgl' or i.name=='gl':
      for j in i.functions:
        code3.append('_%s'%j.name)
  code1.sort()
  code2.sort()
  code3.sort()

  code1.insert( 0, '  SetPixelFormat' )
  code2.insert( 0, '  SetPixelFormat' )

  # RegalMakeCurrent, RegalSetErrorCallback
  code1 += ['  %s' % export for export in additional_exports]
  code2 += ['  %s' % export for export in additional_exports]
  code3 += ['_%s' % export for export in additional_exports]

  outputCode( '%s/Regal.def'  % args.outdir, 'EXPORTS\n' + '\n'.join(code1))
  outputCode( '%s/Regalm.def' % args.outdir, 'EXPORTS\n' + '\n'.join(code2))
  outputCode( '%s/export_list_mac.txt' % args.outdir, '# File: export_list\n' + '\n'.join(code3))
