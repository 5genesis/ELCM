# ELCM (Experiment Life-Cycle Manager)

## Requirements

 - [Python 3.7.x](https://www.python.org)
 - [Optional] [Grafana](https://grafana.com/) (tested on version 5.4)
 - [Optional] [Grafana reporter](https://github.com/IzakMarais/reporter) 
 (tested on version 2.1.0, commit 41b38a0)

## Interoperability with other components

The following information specifies the version that most closely match the expected behavior when this package interacts
with others developed internally in 5 Genesis (i.e. the version that was available during the development and that was 
used while testing this component). It's possible that most (or all) features work with some previous versions, and most
probably there will be no issues when using more recent versions.

 - [Portal](https://gitlab.fokus.fraunhofer.de/5genesis/portal) Version 1.0.8 (29/05/2019)

## Installing (development)
> A video detailing the deployment procedure of the ELCM (and Portal) can be seen [in BSCW](https://bscw.fokus.fraunhofer.de/bscw/bscw.cgi/d3208170/Coordinationlayer_call20190422.mp4)

> It is recommended, but not required, to run the Portal in a [Python virtual environment](https://virtualenv.pypa.io/en/stable/).
> If you are not using virtual environments, skip steps 3 and 4.

1. Clone the repository to a known folder, e.g. in `c:\ELCM` 
2. Enter the folder
```bash
cd c:/ELCM
```
3. Create a new Python virtualenv:
```bash
pip install virtualenv
virtualenv venv
```
4. Activate the virtual environment:
- For Windows:
```powershell
venv\Scripts\Activate.bat
```
- For Linux:
```bash
source venv/bin/activate
```
5. Install Python dependencies:
```bash
pip install -r requirements.txt
```

6. Start the development server:
```bash
flask run
```
The app will generate a default configuration file (`config.yml`) and start listening for requests on port 5001.
Refer to the Configuration section for information about customizing the default values.
Press `Control+C` to stop the development server.

## Deployment (production)

Since the ELCM should not be exposed to the Internet (the administration interface should only be accessed on the host 
machine or from inside a trusted network), and it will not receive a large number of concurrent requests it is possible 
to run the ELCM using the included development server. 

It is, however, also possible to run the ELCM using a production WSGI server such as [Waitress](https://github.com/Pylons/waitress) 
following these instructions:

1. Install Waitress on the ELCM Python environment:
```bash
pip install waitress
```
2. Start the server:
```bash
waitress-serve --listen=*:5001 app:app
```

## Configuration

The ELCM instance can be configured by setting environment variables and by editing the `config.yml` file. The ELCM uses
`python-dotenv`, so it's possible to save the environment variables in the `.flaskenv` file.

The environment variables that can be set are:
* FLASK_RUN_PORT: Port where the ELCM will listen (5000 by default)
* SECRET_KEY: A random string.
> Since the ELCM should not be exposed to the Internet it is not so important to set a random SECRET_KEY. However, the 
value is still **needed** and it's recommended to follow the same approach as with the 5Genesis Portal.

The values that can be configured on `config.yml` are:
* TempFolder: Root folder where the temporal files for the Executors can be created.
* Logging:
    * Folder: Root folder where the different log files will be saved.
    * AppLevel: Minimum log level that will be displayed in the console.
    * LogLevel: Minimum log level that will be recorded in the log files.
* Dispatcher:
    * Host: Location of the machine where the Dispatcher is running (localhost by default).
    * Port: Port where the Dispatcher is listening for connections (5000 by default).
> The Dispatcher does not currently exist as a separate entity, so this information refers to the Portal during Release A.
* Tap: 
    * Enabled: Whether or not to use TAP, if set to False the settings below will be ignored
    * OpenTap: True if using OpenTap (TAP 9), False if using TAP 8
    * Exe: TAP CLI executable
    * Folder: TAP installation folder
    * Results: TAP results folder
    * EnsureClosed: Performs an additional check on test plan completion, to ensure that all child processes are 
    correctly closed. Recommended to set to True, but increases execution time by roughtly 15 seconds.
> These values will be used by the `Run.TapExecute` task.
* Grafana:
    * Enabled
    * Host
    * Port
    * Bearer: Grafana API key without the 'Bearer ' prefix
    * ReportGenerator: URL where the `Grafana reporter` instance can be reached, if any
> These values will be used when generating a dashboard for the results generated by an experiment execution.
* SliceManager:
    * Host
    * Port
> These values will be used to communicate with the Katana Slice Manager when deploying/decommisioning slices and when 
> using the `Run.SliceCreationTime` task. 
* InfluxDb:
    * Enabled: If set to False the settings below will be ignored
    * Host
    * Port
    * User: InfluxDb instance user
    * Password: InfluxDb user password
    * Database: InfluxDb instance database
> These values will be used for sending results to an InfluxDb instance. In particular, they will be used by the
> `Run.SliceCreationTime` task. Additional tags will be generated by using the values in the `Metadata` section
* Metadata:
    * HostIp: IP address of the machine where the ELCM is running
    * Facility: Facility name (or platform)
> Additional ELCM instance metadata, currently used for values sent to InfluxDb

## Facility Configuration

> Starting with version 1.1, the facility is no longer configured by a single `facility.yml` file. UEs must now
> be defined using separate files in the `UEs` sub-folder, while TestCases (and their dashboards) are defined in
> the `TestCases` sub-folder. 
> 
> The available values for each element have not changed, so it's possible to move each key on the `facility.yml` file
> to their respective folders and have the same configuration as before the update.

The contents of the `UEs` and `TestCases` sub-folder describe the behavior of the 5Genesis Platform when an Experiment 
execution request is received. These folders will be automatically generated if they do not exist. The ELCM will load
the contents of every `yml` file contained in these folders on startup and whenever the `Reload facility` button on
the web dashboard is pressed. The dashboard will also display a validation log (`Facility log`) which can be used
in order to detect errors on a TestCase or UE configuration.

* UEs: The files on the `UEs` folder describe the actions to perform when a certain UE is included in the `Experiment descriptor` received
as part of the request (for example, initializing or configuring the UE). The `Composer` will add the actions defined for 
every UE to the Tasks list. The following is an example of a yaml file that configures an UE:

````yaml
TestUE:
    - Order: 1
      Task: Run.Dummy
      Config:
        Message: This is a dummy entity initialization
    - Order: 10
      Task: Run.Dummy
      Config:
        Message: This is a dummy entity closure
```` 

The name of the UE will be extracted from the initial key on the dictionary (not the name of the file). This key contains
a list of every action to perform, described by the relative `Order` in which to run, the `Task` to perform (which 
correspond to the different Tasks defined in the `Executor.Tasks` package) and a `Config` dictionary, which is 
different for every task.

> More information about the composition process can be found in section 3.2 of Deliverable D3.15, please note that
> this example uses the old `facility.yml` file, but the behavior is the same.

* TestCases and Dashboards: Similarly to the UEs, the files in the ´TestCases´ folder define the actions required in 
order to execute a certain TestCase included in the `Experiment descriptor`. The following is an example TestCase file:

````yaml
Slice Creation:
    - Order: 5
      Task: Run.SliceCreationTime
      Config:
        ExperimentId: "@{ExperimentId}"
        WaitForRunning: True
        Timeout: 60
        SliceId: "@{SliceId}"
Dashboard:
    - Name: "Slice Deployment Time"
      Measurement: Slice_Creation_Time
      Field: Slice_Deployment_Time
      Unit: "s"
      Type: Singlestat
      Percentage: False
      Size: [8, 8]
      Position: [0, 0]
      Gauge: True
      Color: ["#299c46", "rgba(237, 129, 40, 0.89)", "#d44a3a"]
      Thresholds: [0, 15, 25, 30]
```` 

The first key ('Slice Creation') follows the same format as un the UEs section, however, these files can contain an 
additional `Dashboard` key that define the list of panels that will be generated as part of the Grafana dashboard
that corresponds to the TestCase. The following values can be set for each panel:

- [Mandatory] `Type`: 'singlestat' (gauges or single value) or 'graph' (time series)
- [Optional]  `Name`: Panel name, '{Measurement}: {Field}' if not set
- [Mandatory] `Measurement`: Measurement (table) name
- [Mandatory] `Field`: Field (column) name
- [Optional]  `Unit`: Field unit
- [Mandatory] `Size`: (As list) [<height>, <width>]
- [Mandatory] `Position`: (As list) [<x>, <y>]
- [Optional]  `Color`: Graph or text color(s). For Gauges this is a list of 3 colors, otherwise a single value. Each color can be defined using these formats: "#rrggbb" or "rgba(rrr, ggg, bbb, a.aa)"

#### For graph:
- [Mandatory] `Lines`: True to display as lines, False to display as bars
- [Mandatory] `Percentage`: Whether the field is a percentage or not
- [Optional]  `Interval`: Time interval of the graph, default $__interval if not set
- [Optional]  `Dots`: Display dots along with the graph or bar

#### For singlestat:
- [Mandatory] `Gauge`: True to display as a gauge, false to display as numeric value
- [Optional]  `MaxValue`: Max expected value of the gauge, 100 if not set
- [Optional]  `MinValue`: Min expected value of the gauge, 0 if not set
 
### Available Tasks:

The following is a list of the tasks that can be defined as part of a TestCase or UE list of actions, as well as their
configuration values:

#### Run.CliExecute
Executes a script or command through the command line. Configuration values:
- `Parameters`: Parameters to pass to the command line (i.e. the line to write on the CLI)
- `CWD`: Working directory where the command will run

#### Run.CompressFiles
Generates a Zip file that contains all the specified files. Configuration values:
- `Files`: List of (single) files to add to the Zip file
- `Folders`: List of folders to search files from. All the files contained within these folders and their sub-folders
will be added to the Zip file
- `Output`: Name of the Zip file to generate. 

#### Run.Dummy
Dummy action, will only display the values on the `Config` dictionary on the log

#### Run.Message
Displays a message on the log, with the configured severity. Configuration values:
- `Severity`: Severity level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- `Message`: Text of the message

#### Run.Publish
Saves a value (identified with a name) for use in another task that runs later. The value can be retrieved using 
variable expansion `@[key]`. If the key is not defined at the time of expansion it will be replaced by the string
`<<UNDEFINED>>` unless another default is defined using `@[key:default]`. In this case the `Config` dictionary
contains the keys and values that will be published. For example, the following tasks:
```yaml
- Order: 5
  Task: Run.Publish
  Config: { Publish1: "Text", Publish2: 1 }
- Order: 10
  Task: Run.Message
  Config: { Severity: INFO, Message: "1: @[Publish1]; 2: @[Publish2]; 3: @[Publish3]; 4: @[Publish4:NoProblem]" }
```
Will produce this message in the log:

`- INFO - 1: Text; 2: 1; 3: <<UNDEFINED>>; 4: NoProblem`

#### Run.SliceCreationTime
Sends the Slice Creation Time reported by the Slice Manager to InfluxDb. Configuration values:
- `ExecutionId`: Id of the execution (can be dinamically expanded from `@{ExecutionId}`)
- `WaitForRunning`: Boolean, wait until the Slice Manager reports that the slice is running, or retrieve results inmediatelly
- `Timeout`: 'WaitForRunning' timeout in (aprox) seconds
- `SliceId`: Slice ID to check (can be dinamically expanded from `@{SliceId}`)

#### Run.TapExecute
Executes a TAP TestPlan, with the possibility of configuring external parameters. Configuration values:
- `TestPlan`: Path (absolute) of the testplan file.
- `GatherResults`: Indicates whether or not to compress the generated CSV files to a Zip file (see below)
- `External`: Dictionary of external parameters 

###### Gathering generated results
If selected, the task will attempt to retrieve all the results generated by the testplan, saving them to a Zip file
that will be included along with the logs once the execution finishes. The task will look for the files in the TAP
Results folder, inside a sub-folder that corresponds with the experiment's execution ID, for this reason, it is 
necessary to add a MultiCSV result listener to TAP that has the following (recommended) `File Path` configuration:
```
Results\{Identifier}\{Date}-{ResultType}-{Identifier}.csv
```

##### Variable expansion

It's possible to expand the value of some variables enclosed by @{ }. (Use quotes where required in order to generate 
valid YAML format). Available values are:
- `@{ExecutionId}:` Experiment execution ID (unique identifier)
- `@{SliceId}`: ID of the slice deployed by the Slice Manager during the PreRun stage
- `@{TempFolder}`: Temporal folder exclusive to the current executor, it's deleted when the experiment finishes.
- `@{TapFolder}`: Folder where the (Open)TAP executable is located (as configured in `config.yml`)
- `@{TapResults}`: Folder where the (Open)TAP results are saved (as configured in `config.yml`)

## PDF Report generation

It's possible to integrate an instance of [Grafana reporter](https://github.com/IzakMarais/reporter) in order to 
generate PDF reports from the Grafana dashboards of the experiments. This feature will appear as a button on the 
top-right of the dashboard.

For using this feature in the ELCM you only need to specify the URL where `Grafana reporter` is reachable. Please refer 
to the reporter documentation for the configuration of the reporter itself. 

The following is an example of a custom template that includes the 5 Genesis branding:

```tex
%use square brackets as golang text templating delimiters
\documentclass{article}
\usepackage{graphicx}
\usepackage[margin=1in]{geometry}
\graphicspath{ {images/} }

\begin{document}
\title{
\includegraphics[scale=1.0]{<<PATH TO 5GENESIS LOGO>>}~\\
5 Genesis [[.Title]] [[if .VariableValues]] \\ \large [[.VariableValues]] [[end]] [[if .Description]] 
%\small [[.Description]] [[end]]}
\date{[[.FromFormatted]] to [[.ToFormatted]]}
\maketitle
\begin{center}
[[range .Panels]][[if .IsSingleStat]]\begin{minipage}{0.3\textwidth}
\includegraphics[width=\textwidth]{image[[.Id]]}
\end{minipage}
[[else]]\par
\vspace{0.5cm}
\includegraphics[width=\textwidth]{image[[.Id]]}
\par
\vspace{0.5cm}
[[end]][[end]]
\end{center}
\end{document}
```
> Remember to specify the correct path to the 5Genesis logo

## REST API

Information about the current REST API of the ELCM (and Portal) can be seen [in BSCW](https://bscw.fokus.fraunhofer.de/bscw/bscw.cgi/d3228781/OpenAPIv1.docx).

## Authors

* **Bruno Garcia Garcia**

## License

TBD