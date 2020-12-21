def deploy_env():
    return "dev"


def env_specific(logical_name):
    if type(logical_name) == str:
        suffix = logical_name
    else:
        suffix = logical_name.name

    return "{}-{}".format(deploy_env(), suffix)


def domain_specific(prefix, logical_name=None):
    if logical_name is None:
        return "{}.{}".format(prefix, deploy_env())
    if deploy_env() != "prod":
        return "{}.{}.{}".format(prefix, deploy_env(), logical_name)
    else:
        return "{}.{}".format(prefix, logical_name)
