**21/10/2019** [Version 1.1.1]

 - Added support for OpenTAP

**02/10/2019** [Version 1.1.0]
 
 - Overhauled configuration procedure (see README.md)
 - Added configuration, facility validation and reload buttons to dashboard 
 - Added support for Katana Slice Manager, automatic instantiation, decommision of slices.
 - Added SliceCreationTime task
 - Added Dots, Color and Threshold configuration values to panels
 - Improved communication between tasks, added Publish task, custom variables expansion

**27/06/2019** [Version 1.0.5]

 - Added support for singlestat (Gauge) Grafana panels
 - Added configurable Name, Unit values to panels
 - Added support for PDF generation using [Grafana reporter](https://github.com/IzakMarais/reporter)

**30/05/2019**

 - Implemented Command Line Executor task for performing actions without TAP. 

**24/05/2019**

 - Implemented Grafana dashboard generation.
 - Send experiment execution status updates to Portal.

**21/05/2019**

 - Added new entrypoint for retrieving an execution's logs
 - Added logic for variable expansion in Task's configuration. Added @ExperimentId variable

**24/04/2019**

Initial merge from UMA repository:
 - Complete logic fur running experiments in parallel, separated in stages and composed by configurable tasks.
 