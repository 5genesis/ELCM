from Task import Task
from Helper import Cli, Level
from os.path import abspath, join, exists
from datetime import datetime, timezone


class RobotFramework(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Robot Framework", parent, params, logMethod, None)
        self.paramRules = {
            'Executable': (None, True),
            'Paths': (None, True),
            'CWD': (None, True),
            'GatherResults': (True, False),
            'Identifier': (None, False)
        }

    def Run(self):
        gatherResults = self.params['GatherResults']
        paths = self.params['Paths']
        if isinstance(paths, str):
            paths = [paths]
        identifier = self.params['Identifier']  # Save to different folders, in case we run multiple instances in a row
        identifier = identifier if identifier is not None else f'RobotFw{datetime.now(timezone.utc).strftime("%H%M%S")}'
        tempFolder = join(abspath(self.parent.TempFolder), identifier)

        parameters = [self.params['Executable']]
        if gatherResults:
            parameters.extend(['--outputdir', tempFolder])
        parameters.extend(paths)

        self.Log(Level.INFO, "Executing Robot Framework tests")
        cli = Cli(parameters, self.params['CWD'], self.Log)
        cli.Execute()
        self.Log(Level.INFO, "Robot Framework tests finished")

        if gatherResults:
            self.Log(Level.INFO, "Gathering test report files")
            found = []
            for kind, path in [('Output', join(tempFolder, 'output.xml')),
                               ('Log', join(tempFolder, 'log.html')),
                               ('Report', join(tempFolder, 'report.html'))]:
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
        else:
            self.Log(Level.INFO, "'GatherResults' disabled: Reports will be generated in the CWD folder")
