# AWS EC2 Instance Type Availability Checker

This script checks the availability of specific EC2 instance types across multiple AWS regions. The script is designed to help you determine where certain instance types are available, categorized as V20 or V10 instances. It also highlights any instance types that are not found in a specific region, which could indicate a problem.

## Instance Types

- **V20 Instances**
  - `c5n.18xlarge` (Controller)
  - `i3en.3xlarge` (Virtual Drive)
  
- **V10 Instances**
  - `c5n.9xlarge` (Controller)
  - `i3.2xlarge` (Virtual Drive)

## AWS Regions

The script checks the following AWS regions:

- `ap-south-1` (Mumbai)
- `ap-south-2` (Hyderabad)
- `ap-northeast-1` (Tokyo)
- `ap-northeast-2` (Seoul)
- `ap-northeast-3` (Osaka)
- `ap-southeast-1` (Singapore)
- `ap-southeast-2` (Sydney)
- `ap-southeast-3` (Jakarta)
- `ap-southeast-4` (Melbourne)
- `ap-southeast-5` (Kuala Lumpur)
- `ap-east-1` (Hong Kong)

## Usage

To run the script, simply copy the following code into your terminal or save it to a `.sh` file and execute it.

### Example Command

```bash
#!/bin/bash

for region in ap-south-1 ap-south-2 ap-northeast-1 ap-northeast-2 ap-northeast-3 ap-southeast-1 ap-southeast-2 ap-southeast-3 ap-southeast-4 ap-southeast-5 ap-east-1; do
    echo "Searching in $region..."
    echo "for V20 Instances"
    for instance_type in c5n.18xlarge i3en.3xlarge; do
        if [[ $instance_type == "c5n.18xlarge" ]]; then
            role="Controller"
        else
            role="Virtual Drive"
        fi
        available=$(aws ec2 describe-instance-type-offerings --filters Name=instance-type,Values=$instance_type --query "InstanceTypeOfferings[].InstanceType" --region $region)
        if [[ $available != "[]" ]]; then
            echo "    v20 $role Instance available \"$instance_type\""
        else
            echo "    **PROBLEM: v20 $role Instance \"$instance_type\" NOT available in $region**"
        fi
    done
    echo "for V10 Instances"
    for instance_type in c5n.9xlarge i3.2xlarge; do
        if [[ $instance_type == "c5n.9xlarge" ]]; then
            role="Controller"
        else
            role="Virtual Drive"
        fi
        available=$(aws ec2 describe-instance-type-offerings --filters Name=instance-type,Values=$instance_type --query "InstanceTypeOfferings[].InstanceType" --region $region)
        if [[ $available != "[]" ]]; then
            echo "    v10 $role Instance available \"$instance_type\""
        else
            echo "    **PROBLEM: v10 $role Instance \"$instance_type\" NOT available in $region**"
        fi
    done
    echo ""
done
```


### Example Output
```bash
Searching in ap-south-1...
for V20 Instances
    v20 Controller Instance available "c5n.18xlarge"
    v20 Virtual Drive Instance available "i3en.3xlarge"
for V10 Instances
    v10 Controller Instance available "c5n.9xlarge"
    v10 Virtual Drive Instance available "i3.2xlarge"

Searching in ap-south-2...
for V20 Instances
    **PROBLEM: v20 Controller Instance "c5n.18xlarge" NOT available in ap-south-2**
    v20 Virtual Drive Instance available "i3en.3xlarge"
for V10 Instances
    **PROBLEM: v10 Controller Instance "c5n.9xlarge" NOT available in ap-south-2**
    v10 Virtual Drive Instance available "i3.2xlarge"
