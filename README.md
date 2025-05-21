Jamf Bulk Prestage Mover is a python based program that runs using only the Requests library found here: https://pypi.org/project/requests/

Specially designed for Northside ISD, the user will input their client credentials specific to the API or previous versions can be found with the client credentials hardcoded. 
After credential verification and getting the token, the user will input each asset tag into the text box with the reflected output list below the inputs.
Users can alternatively input a CSV with their own formatting, so long as the first column are the asset tags. This could be improved with serial number integration.
The user will input the destination prestage name or ID and submit.

The program works by matching the asset tag to the device, stripping the device name to retrieve the serial number, and mapping them to an array. 
This array is then sorted by prestage by stripping the device name of its serial number and matching it to the corresponding prestage. (ex: Hotswap-ipad-stu-XXXXX to NISD-Hotswaps-ipad-stu-ES-PEP)
After stripped, NISD- and -ES-PEP is automatically input to get the device prestage. This is an estimated prestage, the device name does not always exactly correspond to the prestage. 
Jamf API does not currently display the device's prestage under the device info. The device can only be found in the prestage by looking in the predicted prestage. 
Due to this, possible changes include error handling for non-corresponding prestages and nightly prestage scope mapping. 

Prestage Scope Mapping should be nightly as this would search through all prestage scopes resulting in a heavy load with the 30k+ mobile devices. 
This can be stored in a CSV or SQL Database containing Asset Tag, Serial Number, Device Name, Prestage Name, Prestage ID, Version Control Number for Prestage, and Jamf Device ID.
