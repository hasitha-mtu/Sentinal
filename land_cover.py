import os
import subprocess

# Paths
input_dir = "config/S2B_MSIL2A_20241118T115359_N0511_R023_T29UMT_20241118T131020.SAFE"
output_dir = "config"
graph_file = "config/LandCoverClassification.xml"

def land_cover():
    # Loop through Sentinel-2 files
    for file in os.listdir(input_dir):
        if file.endswith(".SAFE"):
            input_file = os.path.join(input_dir, file)
            output_file = os.path.join(output_dir, f"{os.path.splitext(file)[0]}_classified.tif")

            # Run GPT command
            command = [
                "gpt",
                graph_file,
                f"-Pinput={input_file}",
                f"-Poutput={output_file}"
            ]
            subprocess.run(command)

if __name__ == "__main__":
    land_cover()
