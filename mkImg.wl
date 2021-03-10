(* ****************************************************************************
(c) Copyright 2020 Querium Corp. All rights reserved.
This computer program contains Confidential, Proprietary information and is a
Trade Secret of Querium Corp. This document is covered under a Non-Disclosure
Agreement. All use, disclosure, and/or reproduction is prohibited unless
authorized in writing. Copying this software in violation of Federal Copyright
Law is a criminal offense. Deciphering or decompiling the computer program, or
developing or deriving the source code of the computer program, is prohibited.
This computer program may also be protected under laws of non-U.S. countries,
including copyright and trade secret laws.
**************************************************************************** *)

(*******************************************************************************
After cloning the CommonCore repo and checking out gitBranch and gitHash, a
StepWise image is created. The image is used for running tests.

IMPORTANT:
The current working directory still needs to be set to "/path/to/CommonCore"
when the image is used. Otherwise, getGitHash[] will not work!

mkCacheImg expects a string of JSON as an argument and the following fields:
'{
  "dirCommonCore": "/Users/evan/Documents/work/querium/coding/mma/CommonCore",
  "img": "/path/to/stepWise.mx",
 }'

* NOTE:
* Run the script on an ai server:
  /path/to/WolframScript -script mkCacheImg.wl  '{"aField": "aValue"}'

* Run the script on Evan's mac:
  /Applications/Mathematica.app/Contents/MacOS/WolframScript -script /Users/evan/Documents/work/querium/coding/mma/CommonCore/cronjob/cacheServer/mkCacheImg.wl '{"dirCommonCore": "/Users/evan/Documents/work/querium/coding/mma/CommonCore", "img": "/tmp/images", "cachingOn": true, "jsonResponse": true, "redisOn": true, "saveStateInStateOn": true, "autoCachingOn": true, "redisConnTime": 3}'
*******************************************************************************)
Print["- - - - - - - - - - - - - - - - - - - - - - - - - "];
Print[$ProcessID,
      " START: making StepWise image: ",
      DateString["ISODateTime", TimeZone -> 0]];

(*** Acquire command line arguments to be used for configuration in
     building an SW image ***)
(*** MacOS: arguments passed as $ScriptCommandLine ***)
(*** Linux: arguments passed as $CommandLine ***)
Global`$confTesting = <||>;
If[Length[$ScriptCommandLine] > 0,
  Global`$confTesting = ImportString[$ScriptCommandLine[[2]], "RawJSON"];
];
If[Length[Global`$confTesting] < 1 && Length[$CommandLine] > 0,
  Global`$confTesting = ImportString[$CommandLine[[4]], "RawJSON"];
];
If[Length[Global`$confTesting] < 1,
  Print[$ProcessID, " Unable to acquire the command arguments"];
  Exit[4];
];

(*** Display the configuration ***)
(* Scan[Print[#, ": ", Global`$confTesting[#]]&, Keys[Global`$confTesting]]; *)

(*** Verify the directories exist ***)
If[!DirectoryQ[Global`$confTesting["dirCommonCore"]],
  Print[
    $ProcessID,
    " Invalid dir: ", Global`$confTesting["dirCommonCore"]
  ];
  Exit[4];
];

(*** Load Stepwise ***)
SetDirectory[Global`$confTesting["dirCommonCore"]];
Print[$ProcessID, " Loading StepWise ....."];
<< StepWise.m;

(*** configure stepwise settings ***)
Print[$ProcessID, " Configuring StepWise variables ....."];
StepWise`$$InTesting$$ = Global`$confTesting["InTesting"];

(*** Create cache image ***)
Print[$ProcessID, " Creating a new StepWise image ....."];
Share[];
DumpSave[Global`$confTesting["img"],
  {
    "parserMain`", "unitFactor`", "parserDefault`", "parserUnit`",
    "common`", "configParser`", "qccNqA1UntTbls`", "StepWise`", "Global`",
    "$Path", "$RecursionLimit"
  }];

Print[$ProcessID,
      " END: making an image: ",
      DateString["ISODateTime", TimeZone -> 0]];
Exit[];