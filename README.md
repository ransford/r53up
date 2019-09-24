# r53up

Dynamic DNS updates for Amazon Route 53.

You may find this valuable if:

 - You operate an AWS account;
 - You have at least one domain in Route53;
 - You operate endpoints on dynamic IP addresses and would like to refer to them by name.

## Configure AWS

TODO write me in more detail.

Make an IAM user and store its credentials in `~/.aws/credentials`.

Create an IAM group called `dns-updaters` and put the new IAM user in it.

Attach a policy to the group that allows Route53 resource record changes.

Find the Zone ID of the zone you'd like to update.

**NOTE:** because of the permission you assigned to the IAM user you created,
you are giving this otherwise unprivileged account the ability to update
hostnames in your domain. Make sure your AWS credentials are adequately
protected! (`chmod 700 ~/.aws` is a start.)

## Installation of this tool

```shell
$ python3 -m venv .venv
$ .venv/bin/pip install https://github.com/ransford/r53up/archive/master.zip
$ .venv/bin/r53up --help
```

You will typically invoke `r53up` via a crontab entry like this:
```
# crontab -e to edit your crontab
0 */4 * * *	$HOME/r53up/.venv/bin/r53up Z1234567ABCDEF myhostname.dyn.example.com
```
