**30/06/2022** [Version 3.5.0 - Release A]

 - Add Variables parameter to Robot Framework task
 - Update NEF emulator integration to v1.5.0

**13/05/2022** [Version 3.4.0]

 - Add Robot Framework task

**04/05/2022** [Version 3.3.1]

 - Fix SliceId expansion, exception on SingleSliceCreationTime

**01/04/2022** [Version 3.3.0]

 - TestCase definition Version 2

**16/02/2022** [Version 3.2.2]

 - Enhanced PublishFromFile and PublishFromPreviousTaskLog:
   - Make 'Keys' parameter optional
   - Allow setting a Verdict

**14/02/2022** [Version 3.2.1]

 - Fix redirection of command line output (Cli/TapExecute)

**03/02/2022** [Version 3.2.0]

 - Implement Verdict handling
 - Add Evaluate, UpgradeVerdict tasks

**11/11/2021** [Version 3.1.0]

 - Add NEF Emulator handling
 - Add NefLoop task

**05/11/2021** [Version 3.0.1]

 - Implement RestApi, JenkinsJob, JenkinsStatus tasks
 - Add separate EVOLVED-5G configuration file
 - Allow checking the status of finished experiments

**11/10/2021** [Version 3.0.0]

 - Initial EVOLVED-5G release
 - Python 3.10 migration
 - Make communication with Portal optional

**16/07/2021** [Version 2.4.3]

 - Fix network services instantiation
 - Fix csvToInflux exception on Ubuntu 18.04

**08/06/2021** [Version 2.4.2]

 - Allow instantiation of slices without network services or scenario

**12/01/2021** [Version 2.4.1]

 - Updated documentation

**22/12/2020** [Version 2.4.0]

 - Added East/West interface
 - Added support for distributed experiments
 - Added PublishFromFile, PublishFromPreviousLog tasks
 - Improved CsvToInflux task
 - Improved REST debugging
 - Fixed timeout issues
 - Fixed PostRun execution timing

**31/07/2020** [Version 2.3.2]

 - Added Base Slice Descriptor and Scenario handling
 - Added NEST composition
 - Updated Network Slice creation and decommission

**26/06/2020** [Version 2.3.1]

 - Exclusive execution and non-automated experiments
 - Added configurable duration on MONROE experiments
 - New ReservationTime variables

**23/06/2020** [Version 2.3.0]

 - Added SliceCreationTime task supporting iterative deployment of slices using a NEST file.
 - Renamed original SliceCreationTime task to SingleSliceCreationTime.
 - Added CsvToInflux task.

**15/06/2020** [Version 2.2.0]

 - 'Delay' task
 - Local resources handling
 - Network service resources handling
 - Experiment descriptor retrieval endpoint

**13/05/2020** [Version 2.1.0]

 - Updated experiment descriptor
 - Implemented MONROE and custom experiments
 - Added automatic dashboard panel generation

**16/03/2020** [Version 2.0.0]

 - Added CompressFiles task
 - Added functionality for gathering TAP results

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
 