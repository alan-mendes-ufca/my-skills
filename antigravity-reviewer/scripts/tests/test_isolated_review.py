import importlib.util,unittest,pathlib,tempfile,os,sys,io,subprocess
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('m',pathlib.Path(__file__).resolve().parents[1]/'run-isolated-review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Child:
 def __init__(self,code,timed):self.code=code;self.timed=timed;self.pid=99999;self.finished=False;self.waits=[]
 def poll(self):return self.code if self.finished else None
 def wait(self,timeout=None):
  self.waits.append(timeout)
  if self.timed and not self.finished:self.timed=False;raise subprocess.TimeoutExpired('synthetic',timeout)
  self.finished=True;return self.code
class Tests(unittest.TestCase):
 def runmain(self,env=None,context='synthetic /plan untrusted',code=0,response=b'OK',timed=False,bootstrapfail=False):
  roots=[];seen={};closed=[];child=Child(code,timed)
  class TD(tempfile.TemporaryDirectory):
   def __enter__(self):v=super().__enter__();roots.append(v);return v
  def auth(*a):
   if bootstrapfail:raise m.ReviewError('synthetic bootstrap failure')
   return type('Auth',(),{'bus':'/privatebus','close':lambda self:(closed.append(True) or True)})()
  def pop(args,**kwargs):seen['args']=args;seen['stdin']=kwargs['stdin'];kwargs['stdout'].write(response);return child
  output=io.BytesIO()
  with patch.dict(os.environ,env or {},clear=True),patch.object(sys,'argv',['controller',context]),patch.object(sys,'stdout',type('Out',(),{'buffer':output})()),patch.object(m,'binary',lambda n:'/synthetic/'+n),patch.object(m,'elf_dependencies',return_value=('/loader',[])),patch.object(m,'find_ca',return_value='/etc/resolv.conf'),patch.object(m,'bootstrap_auth',auth),patch.object(m,'build_sandbox_args',return_value=['bwrap']),patch.object(m,'close_popen',pop),patch.object(m.tempfile,'TemporaryDirectory',TD),patch.object(m.os,'killpg'):
   try:m.main()
   except SystemExit as e:result=e.code
   except m.ReviewError:result='setupfail'
  self.assertTrue(all(not pathlib.Path(p).exists() for p in roots))
  if roots and not bootstrapfail:self.assertEqual(closed,[True])
  return result,output.getvalue(),seen,child
 def test_mode_and_fixed_prompt(self):
  code,out,s,c=self.runmain();self.assertEqual((code,out),(0,b'OK'));self.assertTrue(s['args'][-1].startswith('/boost '));self.assertNotIn('synthetic /plan untrusted',s['args'][-1]);self.assertEqual(s['stdin'],subprocess.DEVNULL);self.assertEqual(c.waits[0],602)
  code,out,s,c=self.runmain({'ANTIGRAVITY_REVIEW_MODE':'standard'});self.assertEqual(code,0);self.assertIn('--disable-slash-commands',s['args']);self.assertFalse(s['args'][-1].startswith('/boost'))
 def test_error_codes_and_cleanup(self):
  self.assertEqual(self.runmain(code=37)[0],37);self.assertEqual(self.runmain(response=b'')[0],1);self.assertEqual(self.runmain(bootstrapfail=True)[0],'setupfail');self.assertEqual(self.runmain(code=-15)[0],143)
 def test_invalid_inputs(self):
  self.assertEqual(self.runmain(context='  ')[0],2)
  for mode in ('','invalid'):self.assertEqual(self.runmain({'ANTIGRAVITY_REVIEW_MODE':mode})[0],2)
  for timeout in ('','0s','oops'):self.assertEqual(self.runmain({'ANTIGRAVITY_REVIEW_TIMEOUT':timeout})[0],2)
 def test_timeout_override(self):
  code,out,s,c=self.runmain({'ANTIGRAVITY_REVIEW_TIMEOUT':'2s'},timed=True);self.assertEqual(code,124);self.assertEqual(c.waits[0],4);self.assertEqual(s['args'][s['args'].index('--print-timeout')+1],'2s')
 def test_dependency_environment(self):
  with tempfile.TemporaryDirectory() as directory:
   elf=pathlib.Path(directory)/'agy';elf.write_bytes(b'\x7fELF')
   loader=pathlib.Path(directory)/'ld-linux-test';loader.write_bytes(b'')
   result=type('Result',(),{'returncode':0,'stdout':str(loader)+' (0x123)'})()
   with patch.dict(os.environ,{'LD_PRELOAD':'untrusted','LD_LIBRARY_PATH':'untrusted'}),patch.object(m.subprocess,'run',return_value=result) as run:
    m.elf_dependencies(str(elf),'/usr/bin/ldd')
    self.assertEqual(run.call_args.kwargs['env'],{'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'})
 def test_reaped_process_not_signalled(self):
  auth=m.PrivateAuth('/synthetic',{})
  auth.processes=[type('Reaped',(),{'pid':12345,'returncode':0})()]
  with patch.object(m.os,'killpg') as kill:
   self.assertTrue(auth.close())
   kill.assert_not_called()
 def test_transfer_children_removed_before_review(self):
  captured=[];processes=[]
  original_auth=m.PrivateAuth
  class Auth(original_auth):
   def __init__(self,*args):super().__init__(*args);captured.append(self)
  class Process:
   def __init__(self,name):self.name=name;self.pid=12345;self.returncode=None;self.stdout=io.BytesIO(b'SYNTHETIC');self.stdin=io.BytesIO()
   def poll(self):return self.returncode
   def wait(self,timeout=None):
    if self.name=='store':
     self_test.assertTrue(all(p.name!='lookup' for p in captured[0].processes))
    self.returncode=0;return 0
  self_test=self
  with tempfile.TemporaryDirectory() as directory:
   root=pathlib.Path(directory)
   def spawn(args,**kwargs):
    name='lookup' if 'lookup' in args else 'store' if 'store' in args else 'daemon'
    if args[0]=='dbus-daemon':(root/'bus').touch()
    process=Process(name);processes.append(process);return process
   owned=type('Owned',(),{'returncode':0,'stdout':'b true'})()
   bins={name:name for name in ['dbus-daemon','gnome-keyring-daemon','secret-tool','busctl']}
   with patch.object(m,'PrivateAuth',Auth),patch.object(m,'close_popen',spawn),patch.object(m.subprocess,'run',return_value=owned):
    auth=m.bootstrap_auth(root,bins)
    self.assertEqual([p.name for p in auth.processes],['daemon','daemon'])
 def test_no_fds(self):
  with patch.object(m.subprocess,'Popen') as pop:m.close_popen(['synthetic']);self.assertTrue(pop.call_args.kwargs['close_fds']);self.assertEqual(pop.call_args.kwargs['pass_fds'],())
  with self.assertRaises(ValueError):m.close_popen(['synthetic'],pass_fds=(9,))
if __name__ == "__main__": unittest.main()
