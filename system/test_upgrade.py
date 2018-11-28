from utils import *
from indy import did
import pytest
import hashlib
import time
from datetime import datetime, timedelta, timezone
import json
import testinfra
import os


@pytest.mark.asyncio
async def test_pool_upgrade_positive():
    await pool.set_protocol_version(2)
    dests = ['Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv', '8ECVSk179mjsjKRLWiQtssMLgp6EPhWXtaYyStWPSGAb',
             'DKVxG2fXXTU8yT5N7hGEbXB3dfdAnYv1JczDUHpmDxya', '4PS3EDQ3dW1tci1Bp6543CfuuebjFrg36kLAUcskGfaA',
             '4SWokCJWJc69Tn74VvLS6t2G2ucvXqM9FDMsWJjmsUxe', 'Cv1Ehj43DDM5ttNBmC6VPpEfwXWwfGktHwjDJsTV5Fz8',
             'BM8dTooz5uykCbYSAAFwKNkYfT4koomBHsSWHTDtkjhW', '98VysG35LxrutKTNXvhaztPFHnx5u9kHtT7PnUGqDa8x',
             '6pfbFuX5tx7u3XKz8MNK4BJiHxvEcnGRBs1AQyNaiEQL', 'HaNW78ayPK4b8vTggD4smURBZw7icxJpjZvCMLdUueiN',
             '2zUsJuF9suBy2iKkcgmm8uoMB6u5Dq2oHoRuchrZbj2N', 'BXV4SXKEJeYQ8XCRHgpw1Xume5ntqALsRhbUYcF85Mse',
             '71WAtEevzz8aZr8baNJhQCUDLwRhM7LeaErSKNWWKxzn', 'FEUGMFWCSAM725vyH8JZnsitiNUy31NPhugVKb8zDpng',
             'DPZ8GJ1NyNZGJMU6qQZVuBsumY1aVzvcV4FqQK9Y215x', 'FYDoBrDhfGuSwt39Sgd3DZETihpnXy6SzZBggyD9HMrD',
             'EMNhsHNsEpuffxCmgC3fpwVj7LgwtSm3riSizCMN6MBo', 'HD1XnVG6jXqGdmFMDTdJk3AoChxaqTfa6zGLkyXTtHwH',
             'DUGXi5vxRZcrDC8VPZFU6bpiHDMhnWic9tDaoDJv3Bj6', 'D7jphMASPQAD6UFvT2ULjEfYybCJVDzwvfG5ZWJoXa69',
             '7vcRBffPvKuGQz4F1ThYAo3Ucq3rXgU62enf6d23u8KX', 'DfSoxVHbbdZrAmwTJcRqM2arwUSvK3L6PXjqWHGo58xD',
             'FTBmYnhxVd8zXZFRzca5WFKh7taW9J573T8pXEWL8Wbb', 'EjZrHfLTBR38d67HasBxpyKRBvrPBJ5RiAMubPWXLxWr',
             'koKn32jREPYR642DQsFftPoCkTf3XCPcfvc3x9RhRK7'
             ]
    init_time = -150
    version = '1.6.706'
    name = 'upgrade'+'_'+version+'_'+datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
    action = 'start'
    _sha256 = hashlib.sha256().hexdigest()
    _timeout = 10
    docker_4_schedule = json.dumps(dict(
        {dest:
            datetime.strftime(datetime.now(tz=timezone.utc) + timedelta(minutes=init_time+i*5), '%Y-%m-%dT%H:%M:%S%z')
         for dest, i in zip(dests[:4], range(len(dests[:4])))}
    ))
    aws_25_schedule = json.dumps(dict(
        {dest:
            datetime.strftime(datetime.now(tz=timezone.utc) + timedelta(minutes=init_time+i*5), '%Y-%m-%dT%H:%M:%S%z')
         for dest, i in zip(dests, range(len(dests)))}
    ))
    reinstall = False
    force = True
    # package = 'indy-node'
    pool_handle, _ = await pool_helper(path_to_genesis='./aws_genesis')
    wallet_handle, _, _ = await wallet_helper()
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))

    req = await ledger.build_pool_upgrade_request(trustee_did, name, version, action, _sha256, _timeout,
                                                  aws_25_schedule, None, reinstall, force, None)
    res = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req))
    print(res)

    time.sleep(120)

    docker_4_hosts = [testinfra.get_host('docker://node' + str(i)) for i in range(1, 5)]
    aws_25_hosts = [testinfra.get_host('ssh://auto_node'+str(i),
                                       ssh_config='/home/indy/indy-node/pool_automation/auto/.ssh/ssh_config')
                    for i in range(1, 26)]
    print(aws_25_hosts)
    os.chdir('/home/indy/indy-node/pool_automation/auto/.ssh/')
    outputs = [host.run('dpkg -l | grep indy-node') for host in aws_25_hosts]
    print(outputs)
    os.chdir('/home/indy/PycharmProjects/tests')
    checks = [output.stdout.find(version) for output in outputs]
    print(checks)
    for check in checks:
        assert check is not -1