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
Print[$ProcessID, " START: making StepWise image: ", DateString[]];
(*Print["Print[$CommandLine]: ", $ScriptCommandLine];*)

(*** Read JSON argument ***)
Global`$confCache = ImportString[$ScriptCommandLine[[2]], "RawJSON"];
Scan[Print[#, ": ", Global`$confCache[#]]&, Keys[Global`$confCache]];

(*** Verify the directories exist ***)
If[!DirectoryQ[Global`$confCache["dirCommonCore"]],
  Print[
    $ProcessID,
    " Invalid dir: ", Global`$confCache["dirCommonCore"]
  ];
  Exit[4];
];

(*** Load Stepwise ***)
SetDirectory[Global`$confCache["dirCommonCore"]];
Print[$ProcessID, " Loading StepWise ....."];
<< StepWise.m;

(*** configure stepwise settings ***)
Print[$ProcessID, " Configuring StepWise variables ....."];
StepWise`$$InTesting$$ = Global`$confCache["InTesting"];

(*** Delete cache image file if it already exists ***)
If[FileExistsQ[Global`$confCache["img"]],
  DeleteFile[Global`$confCache["img"]];
  Print[$ProcessID, " Deleted old cache image"];
];

(*** Create cache image ***)
Print[$ProcessID, " Creating a new StepWise image ....."];
Share[];
DumpSave[Global`$confCache["img"],
  {
    "parserMain`", "unitFactor`", "parserDefault`", "parserUnit`",
    "common`", "configParser`", "qccNqA1UntTbls`", "StepWise`", "Global`",
    "$Path", "$RecursionLimit"
  }];

Print[$ProcessID, " END: making an image: ", DateString[]];
Exit[];