#!/bin/bash
INPUT_DIR="config/S2B_MSIL2A_20241118T115359_N0511_R023_T29UMT_20241118T131020.SAFE"
OUTPUT_DIR="config"
GRAPH_FILE="config/LandCoverClassification.xml"


(base) PS C:\Users\AdikariAdikari\PycharmProjects\Sentinal\config> gpt config/LandCoverClassification.xml -Pinput="config/S2B_MSIL2A_20241118T115359_N0511_R023_T29UMT_20241118T131020.SAFE" -Poutput="output.tif"
WARNING: An illegal reflective access operation has occurred
WARNING: Illegal reflective access by org.esa.snap.runtime.Engine (file:/C:/Program%20Files/esa-snap/snap/modules/ext/org.esa.snap.snap-core/org-esa-snap/snap-runtime.jar) to method java.lang.ClassLoader.initializePath(java.lang.String)
WARNING: Please consider reporting this to the maintainers of org.esa.snap.runtime.Engine
WARNING: Use --illegal-access=warn to enable warnings of further illegal reflective access operations
WARNING: All illegal access operations will be denied in a future release
INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.

Error: config\LandCoverClassification.xml (The system cannot find the path specified)
java.io.FileNotFoundException: config\LandCoverClassification.xml (The system cannot find the path specified)
        at java.base/java.io.FileInputStream.open0(Native Method)
        at java.base/java.io.FileInputStream.open(FileInputStream.java:219)
        at java.base/java.io.FileInputStream.<init>(FileInputStream.java:157)
        at java.base/java.io.FileInputStream.<init>(FileInputStream.java:112)
        at java.base/java.io.FileReader.<init>(FileReader.java:60)
        at org.esa.snap.core.gpf.main.DefaultCommandLineContext.createReader(DefaultCommandLineContext.java:130)
        at org.esa.snap.core.gpf.main.DefaultCommandLineContext.readGraph(DefaultCommandLineContext.java:103)
        at org.esa.snap.core.gpf.main.CommandLineTool.readGraph(CommandLineTool.java:569)
        at org.esa.snap.core.gpf.main.CommandLineTool.runGraph(CommandLineTool.java:346)
        at org.esa.snap.core.gpf.main.CommandLineTool.runGraphOrOperator(CommandLineTool.java:287)
        at org.esa.snap.core.gpf.main.CommandLineTool.run(CommandLineTool.java:188)
        at org.esa.snap.core.gpf.main.CommandLineTool.run(CommandLineTool.java:121)
        at org.esa.snap.core.gpf.main.GPT.run(GPT.java:60)
        at org.esa.snap.core.gpf.main.GPT.main(GPT.java:37)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:566)
        at org.esa.snap.runtime.Launcher.lambda$run$0(Launcher.java:55)
        at org.esa.snap.runtime.Engine.runClientCode(Engine.java:189)
        at org.esa.snap.runtime.Launcher.run(Launcher.java:51)
        at org.esa.snap.runtime.Launcher.main(Launcher.java:31)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:566)
        at com.exe4j.runtime.LauncherEngine.launch(LauncherEngine.java:84)
        at com.exe4j.runtime.WinLauncher.main(WinLauncher.java:94)
        at com.install4j.runtime.launcher.WinLauncher.main(WinLauncher.java:25)
(base) PS C:\Users\AdikariAdikari\PycharmProjects\Sentinal\config>
(base) PS C:\Users\AdikariAdikari\PycharmProjects\Sentinal\config>
(base) PS C:\Users\AdikariAdikari\PycharmProjects\Sentinal\config>
(base) PS C:\Users\AdikariAdikari\PycharmProjects\Sentinal\config> pwd

Path
----
C:\Users\AdikariAdikari\PycharmProjects\Sentinal\config

gpt C:\Users\AdikariAdikari\PycharmProjects\Sentinal\config\LandCoverClassification.xml -Pinput="C:\Users\AdikariAdikari\PycharmProjects\Sentinal\config\S2B_MSIL2A_20241118T115359_N0511_R023_T29UMT_20241118T131020.SAFE" -Poutput="output.tif"

for FILE in $INPUT_DIR/*.SAFE; do
    BASENAME=$(basename $FILE .SAFE)
    OUTPUT_FILE="$OUTPUT_DIR/${BASENAME}_classified.tif"
    gpt $GRAPH_FILE -Pinput=$FILE -Poutput=$OUTPUT_FILE
done
