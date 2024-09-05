# AWS EC2 Instance Type Availability Checker

This script checks the availability of specific EC2 instance types across multiple AWS regions. The script is designed to help you determine where certain instance types are available, categorized as V20 or V10 instances.

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

To run the script, simply copy the following code into your terminal.

### Example Command

```bash
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
        fi
    done
    echo ""
done
