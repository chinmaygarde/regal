#!/usr/bin/python -B

from string import Template, upper, replace

from ApiUtil    import outputCode
from ApiCodeGen import *

from RegalContextInfo import cond

##############################################################################################

enumHeaderTemplate = Template( '''${AUTOGENERATED}
${LICENSE}

#ifndef __${HEADER_NAME}_H__
#define __${HEADER_NAME}_H__

#include "RegalUtil.h"

REGAL_GLOBAL_BEGIN

#include <GL/Regal.h>

REGAL_GLOBAL_END

REGAL_NAMESPACE_BEGIN

enum Enum {
${REGAL_ENUM}
};

REGAL_NAMESPACE_END

#endif
''')

def generateEnumHeader(apis, args):

  regalEnumSet = set()
  regalEnum = []

  for i in apis:
    if i.name == 'gl':
      for enum in i.enums:
        if enum.name == 'defines':
          for enumerant in enum.enumerants:
            if not enumerant.name in regalEnumSet:
              regalEnumSet.add(enumerant.name)
              regalEnum.append(enumerant.name)

  # GL_TIMEOUT_IGNORED 0xffffffffffffffff can't be represented as an enum

  regalEnum = [ '   R%s = %s,'%(i,i) for i in regalEnum if i not in [ 'GL_TIMEOUT_IGNORED' ] ]

  substitute = {}
  substitute['LICENSE']       = args.license
  substitute['AUTOGENERATED'] = args.generated
  substitute['COPYRIGHT']     = args.copyright
  substitute['REGAL_ENUM']    = '\n'.join(regalEnum)
  substitute['HEADER_NAME']   = "REGAL_ENUM"

  outputCode( '%s/RegalEnum.h' % args.outdir, enumHeaderTemplate.substitute(substitute))

