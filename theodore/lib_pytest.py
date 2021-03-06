"""
General tools for using pytest.
"""

import os, shutil, subprocess, difflib

class pytest_job:
    """
    Run and check job in EXAMPLES directory using pytest.
    """
    def __init__(self, cfile):
        self.wstring = ''
        self.epath = os.path.dirname(os.path.abspath(cfile))
        self.prep()

    def run_standard(self):
        """
        Run tests in standard format.
        TODO: one can include custom bash files here
        """
        os.chdir(self.epath + '/RUN')
        for ifile in sorted(os.listdir('../IN_FILES')):
            print(ifile)
            shutil.copy("../IN_FILES/"+ifile, ifile)
            
            finfo = ifile.split('.')
            dtype = finfo[0]
            atype = finfo[2]
            comm="analyze_%s.py"%dtype
            
            with open("analyze_%s.out"%atype, 'w') as outf:
                subprocess.check_call([comm, "-f", ifile], stdout=outf)
            # if dtype == 'tden':
            #     sys.argv = ['analyze_tden.py']
            #     import analyze_tden

        self.check()

    def prep(self):
        os.chdir(self.epath)
        if os.path.exists('RUN'):
            shutil.rmtree('RUN')
        shutil.copytree('QC_FILES', 'RUN')
        os.chdir(self.epath + '/RUN')

    def check(self):
        """
        Check if there are any differences.
        """
        os.chdir(self.epath + '/RUN')
        print("Checking primary output files")
        for rfile in os.listdir('../REF_FILES'):
            print("  -> " + rfile)
            self.file_diff('../REF_FILES/'+rfile, rfile)

        if len(self.wstring) > 0:
            raise pytestDiffError(self.epath + '\n\n' + self.wstring)

    def file_diff(self, reff, runf):
        """
        Check if the files are different.
         line-by-line treatment for txt files, otherwise general diff.
        """
        wstring = "\n"
        
        ref = open(reff).readlines()
        run = open(runf).readlines()
#        suffix = runf.split('.')[-1]

        # These files should match line-by-line
        if '.txt' in runf:
            for iline, line in enumerate(ref):
                if not line == run[iline]:
                    # TODO: one could add numerical thresholds here
                    self.wstring += "- " + line
                    self.wstring += "+ " + run[iline]
        # Use a general diff here
        else:
            diffl = list(difflib.unified_diff(self.diff_ignore(ref), self.diff_ignore(run), fromfile=reff, tofile=runf))
            if len(diffl) > 0:
                wstring = "\n"
                for line in diffl:
                    self.wstring += line

    def diff_ignore(self, dlist):
        outl = []
        iglist = ["TheoDORE", "time", "rbkit", "openbabel", "capabilities"]
        for line in dlist:
            for ig in iglist:
                if ig in line:
                    break
                elif line.strip() == "":
                    break
            else:
                outl.append(line)
        return outl

class pytestDiffError(Exception):
    def __init__(self, errmsg):
        self.errmsg = errmsg
        
    def __str__(self):
        return "\n\n *** pytest detected difference to reference results: ***\n\n %s"%self.errmsg