# AWS-Automation
AWS Automation for smart and cost effective deletion of services

Demo Video : https://drive.google.com/file/d/1pS93gbIblYgbMc_gBhE6Zozs21IyppRa/view?usp=sharing

- You need to create a load balancer
- Create Six Lambda Functions with given python codes (These codes are specific to AWS Lambda)
- Add each of the Lambda Functions to corresponding to Load Balancer Rules (in path):
    - Default_Webpage.py      :     Default Rule of ALB
    - CF_Stack_Deletion.py    :     /cfdelete
    - EC2_Terminate.py        :     /ec2terminate
    - Load_Balancer_Deletion.py:    /albdelete and /elbdelete
    - RDS_Deletion.py         :     /rdsdelete
    - Security_Group_Deletion.py:   /sgdelete
 
 - Follow the instruction manual
