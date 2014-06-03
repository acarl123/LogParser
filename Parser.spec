# -*- mode: python -*-
a = Analysis(['mainapp.py'],
             pathex=['C:\\workdir\\IPEM_Timing_Proto\\GUI'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Parser.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False )
