def deploy_env():
  return "dev"

def env_specific(logical_name):
    if type(logical_name) == str:
        suffix = logical_name
    else:
        suffix = logical_name.name

    return '{}-{}'.format(deploy_env(), suffix)