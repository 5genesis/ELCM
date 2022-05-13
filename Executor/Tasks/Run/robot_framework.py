from Task import Task
from Helper import Cli, Level
from os.path import abspath, join, exists
from datetime import datetime, timezone
import xml.etree.ElementTree as ET


class RobotFramework(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Robot Framework", parent, params, logMethod, None)
        self.paramRules = {
            'Executable': (None, True),
            'Paths': (None, True),
            'CWD': (None, True),
            'GatherResults': (True, False),
            'Identifier': (None, False),
            'VerdictOnPass': ("Pass", False),
            'VerdictOnFail': ("Fail", False)
        }

    def Run(self):
        from Executor import Verdict

        gatherResults = self.params['GatherResults']
        paths = self.params['Paths']
        if isinstance(paths, str):
            paths = [paths]
        identifier = self.params['Identifier']  # Save to different folders, in case we run multiple instances in a row
        identifier = identifier if identifier is not None else f'RobotFw{datetime.now(timezone.utc).strftime("%H%M%S")}'
        tempFolder = join(abspath(self.parent.TempFolder), identifier)
        onPass = self.GetVerdictFromName(self.params["VerdictOnPass"])
        onFail = self.GetVerdictFromName(self.params["VerdictOnFail"])

        parameters = [self.params['Executable'], '--xunit', 'xunit.xml']
        if gatherResults:
            parameters.extend(['--outputdir', tempFolder])
        parameters.extend(paths)

        try:
            self.Log(Level.INFO, "Executing Robot Framework tests")
            cli = Cli(parameters, self.params['CWD'], self.Log)
            cli.Execute()
            self.Log(Level.INFO, "Robot Framework tests finished")
        except Exception as e:
            self.SetVerdictOnError()
            raise RuntimeError(f"Exception while executing Robot Framework: {e}") from e

        fullXml = join(tempFolder, 'output.xml')
        if onPass != Verdict.NotSet or onFail != Verdict.NotSet:
            try:
                self.Log(Level.INFO, "Generating verdict from test results")
                xml = ET.parse(fullXml)
                total = xml.getroot().find("./statistics/total/stat")
                if total is not None:
                    success = int(total.attrib['pass'])
                    fail = int(total.attrib['fail'])
                    skip = int(total.attrib['skip'])
                    self.Verdict = onPass if fail == 0 else onFail
                    self.Log(Level.INFO,
                             f"Verdict set to {self.Verdict.name} (pass: {success}, fail: {fail}, skip: {skip})")
                else:
                    raise RuntimeError("Could not find total statistics in output.xml")
            except Exception as e:
                self.SetVerdictOnError()
                raise RuntimeError(f"Exception while generating verdict: {e}") from e

        else:
            self.Log(Level.INFO, "Skipping Verdict generation")

        if gatherResults:
            try:
                self.Log(Level.INFO, "Gathering test report files")
                found = []
                for kind, path in [('Output', fullXml),
                                   ('Log', join(tempFolder, 'log.html')),
                                   ('Report', join(tempFolder, 'report.html')),
                                   ('xUnit compatible', join(tempFolder, 'xunit.xml'))]:
                    if exists(path):
                        found.append(path)
                    else:
                        self.Log(Level.WARNING, f'Could not retrieve {kind} file ({path})')
                if len(found) > 0:
                    from Helper import Compress
                    path = join(abspath(self.parent.TempFolder), f"{identifier}.zip")
                    Compress.Zip(found, path, flat=True)
                    self.parent.GeneratedFiles.append(path)
                    self.Log(Level.INFO, f"Report files compressed to '{identifier}.zip'")
                else:
                    self.Log(Level.WARNING, "No report files found, skipping zip creation.")
            except Exception as e:
                self.SetVerdictOnError()
                raise RuntimeError(f"Exception while gathering generated files: {e}") from e
        else:
            self.Log(Level.INFO, "'GatherResults' disabled: Reports will be generated in the CWD folder")
