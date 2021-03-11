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
runTask.wl is called from testServer.py to run a test path.

IMPORTANT:
The current working directory still needs to be set to "/path/to/CommonCore"
when a StepWise image is used. Otherwise, getGitHash[] will not work!

runTask.wl expects a JSON in a string form as an argument and the following
fields are present:
dbConn.getFields('testPath')

* NOTE:
* Run the script on an ai server:
  /path/to/WolframScript -script runCaching.wl  '{"aField": "aValue"}'

* Run the script on Evan's mac:
  /Applications/Mathematica.app/Contents/MacOS/WolframScript -script /Users/evan/Documents/work/querium/coding/python/testServer/runTask.wl '{"dirCommonCore": "/tmp/stepwise/28746af9688a13aca6084ba8a1833b9f5a682601/CommonCore", "img": "/tmp/stepwise/28746af9688a13aca6084ba8a1833b9f5a682601/images/cacheImg.mx", "loadFromImgOn": true}'
*******************************************************************************)

(*** Upload the result ***)
uploadTestResult[aTask_Association, data_Association] :=
    Module[{tbl="testPath", dataToDb=<||>, flds, vals={}, tmp={}},
      (** Get valid fields of the tbl **)
      flds=StepWise`getAttrOf[tbl];

      (** Update dataToDb with data **)
      If[MemberQ[flds, #], dataToDb[#]=data[#]]& /@Keys[data];

      If[TrueQ[data["status"]],
        dataToDb["status"] = "success";
        (** Make sure the keys in data are valid ones for testPath **)
        (If[MemberQ[flds, #], dataToDb[#]=data["result"][#]])&
            /@Keys[data["result"]];
        ,
        dataToDb["status"] = "fail";
        dataToDb["msg"] = If[StringQ[data["result"]], data["result"], ""];
      ];

      (** Round up float to integer **)
      If[KeyExistsQ[dataToDb, "timeCompleted"],
        dataToDb["timeCompleted"] = Ceiling[dataToDb["timeCompleted"]]];

      (** Update the testPath table **)
      mysqlConn`mysqlUpdateTblMult[
        StepWise`getDbConn[],
        tbl, "id", aTask["id"], Keys[dataToDb], Values[dataToDb]]
    ];

(*** Main Logic ***)

(*** Read task information from command line as a JSON argument ***)
$testTask = <||>;
If[Length[$ScriptCommandLine] > 0,
  $testTask = ImportString[$ScriptCommandLine[[2]], "RawJSON"];
];
If[Length[$testTask] < 1 && Length[$CommandLine] > 0,
  $testTask = ImportString[$CommandLine[[4]], "RawJSON"];
];
If[Length[$testTask] < 1,
  Print[$ProcessID, " Failed to acquire the task as a command argument"];
  Exit[4];
];

(*** Verify the directories exist ***)
If[!DirectoryQ[$testTask["dirCommonCore"]],
  Print[$ProcessID, " Invalid path to dirCommonCore"];
  Exit[4];
];

(*** If StepWise is loaded from an image, make sure it exists ***)
If[$testTask["loadFromImgOn"] && !FileExistsQ[$testTask["img"]],
  Print[$ProcessID, " Missing the cache image: ", $testTask["img"]];
  Exit[5];
];

(*** Load Stepwise ***)
SetDirectory[$testTask["dirCommonCore"]];
If[TrueQ[$testTask["loadFromImgOn"]],
  Print[$ProcessID, " Loading StepWise from an image ....."];
  Get[$testTask["img"]]
  ,
  Print[$ProcessID, " Loading StepWise without an image ....."];
  << StepWise.m;
];

(*** Configure global settings ***)
(* StepWise`$$InTesting$$ = $testTask["inTesting"] - inTesting should come from testPath *)
StepWise`$$InTesting$$ = True

(*** Update the testPath table ***)
Get[FileNameJoin[{$testTask["dirCommonCore"], "include", "mysqlConn.m"}]];
currTime = DateString["ISODateTime", TimeZone -> 0];
dbStatus = StepWise`modTestPath[$testTask["id"],
  {"pid", "status", "started"},
  {$ProcessID, "running", currTime}
];
If[dbStatus =!= 1,
  Print[$ProcessID, " Failed to update testPath with pid, status, started"];
  Exit[7];
];
Print[$ProcessID, " STARTED - Task ", $testTask["id"], " at ", currTime];

(*** Run testing ***)
testRslt = StepWise`runTestTask[$testTask];
If[!AssociationQ[testRslt],
  testRslt = <|
    "status"->False,
    "result"->"CommonCore failed to run the task"
  |>;
  Print[$ProcessID, " ", testRslt["result"], ": ", $testTask["id"]];
];

(*** Update the result in the testPath table ***)
testRslt["finished"] = DateString["ISODateTime", TimeZone -> 0];
dbStatus = uploadTestResult[$testTask, testRslt];
If[dbStatus =!= 1,
  Print[$ProcessID, " Failed to upload the result of task ", $testTask["id"]];
  Exit[7];
];

Print[$ProcessID, " END - testing: "];
Exit[];