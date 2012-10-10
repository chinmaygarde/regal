from builder import builder
Import('libenv')

regal = libenv.Clone()

# regal.Append(CCFLAGS = [
#     '-finstrument-functions'
# ])

regal.Append(CPPDEFINES = [
    'REGAL_NO_PNG',
])

regal.Append(CPPPATH = [
    './',
    '#Library',
    'src/glu/include',
    'include',
    'include/GL',
    'src/glu/libnurbs/internals',
    'src/glu/libnurbs/interface',
    'src/glu/libnurbs/nurbtess',
    'src/glew/include',
])

# regal Sources
sources = [
    # Regal
    'src/regal/RegalIff.cpp',
    'src/regal/Regal.cpp',
    'src/regal/RegalToken.cpp',
    'src/regal/RegalLog.cpp',
    'src/regal/RegalInit.cpp',
    'src/regal/RegalUtil.cpp',
    'src/regal/RegalConfig.cpp',
    'src/regal/RegalLookup.cpp',
    'src/regal/RegalHelper.cpp',
    'src/regal/RegalMarker.cpp',
    'src/regal/RegalContext.cpp',
    'src/regal/RegalContextInfo.cpp',
    'src/regal/RegalDispatchGlobal.cpp',
    'src/regal/RegalDispatcher.cpp',
    'src/regal/RegalDispatchEmu.cpp',
    'src/regal/RegalDispatchLog.cpp',
    'src/regal/RegalDispatchDebug.cpp',
    'src/regal/RegalDispatchError.cpp',
    'src/regal/RegalDispatchLoader.cpp',
    'src/regal/RegalDispatchNacl.cpp',
    'src/regal/RegalDispatchStaticES2.cpp',
    'src/regal/RegalDispatchStaticEGL.cpp',
    'src/regal/RegalDispatchMissing.cpp',
    'src/regal/RegalHttp.cpp',
    'src/regal/RegalFavicon.cpp',
    'src/md5/src/md5.c',

    # GLU
    'src/glu/libtess/dict.c',
    'src/glu/libtess/geom.c',
    'src/glu/libtess/memalloc.c',
    'src/glu/libtess/mesh.c',
    'src/glu/libtess/normal.c',
    'src/glu/libtess/priorityq.c',
    'src/glu/libtess/render.c',
    'src/glu/libtess/sweep.c',
    'src/glu/libtess/tess.c',
    'src/glu/libtess/tessmono.c',
    'src/glu/libutil/error.c',
    'src/glu/libutil/glue.c',
    'src/glu/libutil/mipmap.c',
    'src/glu/libutil/project.c',
    'src/glu/libutil/quad.c',
    'src/glu/libutil/registry.c',
    'src/glu/libnurbs/interface/bezierEval.cc',
    'src/glu/libnurbs/interface/bezierPatch.cc',
    'src/glu/libnurbs/interface/bezierPatchMesh.cc',
    'src/glu/libnurbs/interface/glcurveval.cc',
    'src/glu/libnurbs/interface/glinterface.cc',
    'src/glu/libnurbs/interface/glrenderer.cc',
    'src/glu/libnurbs/interface/glsurfeval.cc',
    'src/glu/libnurbs/interface/incurveeval.cc',
    'src/glu/libnurbs/interface/insurfeval.cc',
    'src/glu/libnurbs/internals/arc.cc',
    'src/glu/libnurbs/internals/arcsorter.cc',
    'src/glu/libnurbs/internals/arctess.cc',
    'src/glu/libnurbs/internals/backend.cc',
    'src/glu/libnurbs/internals/basiccrveval.cc',
    'src/glu/libnurbs/internals/basicsurfeval.cc',
    'src/glu/libnurbs/internals/bin.cc',
    'src/glu/libnurbs/internals/bufpool.cc',
    'src/glu/libnurbs/internals/cachingeval.cc',
    'src/glu/libnurbs/internals/ccw.cc',
    'src/glu/libnurbs/internals/coveandtiler.cc',
    'src/glu/libnurbs/internals/curve.cc',
    'src/glu/libnurbs/internals/curvelist.cc',
    'src/glu/libnurbs/internals/curvesub.cc',
    'src/glu/libnurbs/internals/dataTransform.cc',
    'src/glu/libnurbs/internals/displaylist.cc',
    'src/glu/libnurbs/internals/flist.cc',
    'src/glu/libnurbs/internals/flistsorter.cc',
    'src/glu/libnurbs/internals/hull.cc',
    'src/glu/libnurbs/internals/intersect.cc',
    'src/glu/libnurbs/internals/knotvector.cc',
    'src/glu/libnurbs/internals/mapdesc.cc',
    'src/glu/libnurbs/internals/mapdescv.cc',
    'src/glu/libnurbs/internals/maplist.cc',
    'src/glu/libnurbs/internals/mesher.cc',
    'src/glu/libnurbs/internals/monotonizer.cc',
    'src/glu/libnurbs/internals/monoTriangulationBackend.cc',
    'src/glu/libnurbs/internals/mycode.cc',
    'src/glu/libnurbs/internals/nurbsinterfac.cc',
    'src/glu/libnurbs/internals/nurbstess.cc',
    'src/glu/libnurbs/internals/patch.cc',
    'src/glu/libnurbs/internals/patchlist.cc',
    'src/glu/libnurbs/internals/quilt.cc',
    'src/glu/libnurbs/internals/reader.cc',
    'src/glu/libnurbs/internals/renderhints.cc',
    'src/glu/libnurbs/internals/slicer.cc',
    'src/glu/libnurbs/internals/sorter.cc',
    'src/glu/libnurbs/internals/splitarcs.cc',
    'src/glu/libnurbs/internals/subdivider.cc',
    'src/glu/libnurbs/internals/tobezier.cc',
    'src/glu/libnurbs/internals/trimline.cc',
    'src/glu/libnurbs/internals/trimregion.cc',
    'src/glu/libnurbs/internals/trimvertpool.cc',
    'src/glu/libnurbs/internals/uarray.cc',
    'src/glu/libnurbs/internals/varray.cc',
    'src/glu/libnurbs/nurbtess/directedLine.cc',
    'src/glu/libnurbs/nurbtess/gridWrap.cc',
    'src/glu/libnurbs/nurbtess/monoChain.cc',
    'src/glu/libnurbs/nurbtess/monoPolyPart.cc',
    'src/glu/libnurbs/nurbtess/monoTriangulation.cc',
    'src/glu/libnurbs/nurbtess/partitionX.cc',
    'src/glu/libnurbs/nurbtess/partitionY.cc',
    'src/glu/libnurbs/nurbtess/polyDBG.cc',
    'src/glu/libnurbs/nurbtess/polyUtil.cc',
    'src/glu/libnurbs/nurbtess/primitiveStream.cc',
    'src/glu/libnurbs/nurbtess/quicksort.cc',
    'src/glu/libnurbs/nurbtess/rectBlock.cc',
    'src/glu/libnurbs/nurbtess/sampleComp.cc',
    'src/glu/libnurbs/nurbtess/sampleCompBot.cc',
    'src/glu/libnurbs/nurbtess/sampleCompRight.cc',
    'src/glu/libnurbs/nurbtess/sampleCompTop.cc',
    'src/glu/libnurbs/nurbtess/sampledLine.cc',
    'src/glu/libnurbs/nurbtess/sampleMonoPoly.cc',
    'src/glu/libnurbs/nurbtess/searchTree.cc',

    # GLEW
    'src/glew/src/glew.c',

    # GLEWinfo
    'src/glew/src/glewinfo.c',
]

non_sources = [
]

library = builder.BuildLibrary(regal, 'Regal', sources)
Return('library')
