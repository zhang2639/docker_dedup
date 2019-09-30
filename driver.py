"""Nitro: proxy driver entry point
Usage:
    driver.py [--config-file <config-file>]

Arguments:
    <config-file> path to the configuration file
"""

def run(config_file):
    from global_configuration import NitroConfiguration
    cfg = NitroConfiguration(config_file)

    cfg.logger.info("Driver starting..")

    from app_factory import AppFactory
    factory = AppFactory(cfg)
    try:
        factory.build()
        factory.start()
        cfg.logger.info("Driver exiting..")
        return 0
    except Exception as e:
        print "driver: Exception -> ", e
        cfg.logger.exception(e)
        raise e
    finally:
        print "Exiting.."
        cfg.logger.info("Exiting..")
        import logging
        logging.shutdown()


if __name__ == "__main__":
    import sys
    from docopt import docopt
    arguments = docopt(__doc__, version='0.1.0')
    config_file = arguments["<config-file>"] if arguments["--config-file"] \
                    else "/etc/nitro/nitro.yaml"
    print "config file:", config_file
    sys.exit(run(config_file))