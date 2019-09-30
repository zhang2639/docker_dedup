"""Nitro: networking driver
Usage:
    comm-driver.py [--config-file <config-file>]

Arguments:
    <config-file> path to the configuration file
"""

def run(config_file):
    from global_configuration import NitroConfiguration
    cfg = NitroConfiguration(config_file)

    try:
        from networking.p2p import PeerNode
        node = PeerNode(cfg)

        from graceful_killer import GracefulKiller
        killer = GracefulKiller('p2p', [node])
        killer.register()

        from throughput import ThroughputTestServer
        tt_server = ThroughputTestServer()
        tt_server.start()

        node.start()
        return 0
    except Exception as e:
        print "comm-driver: Exception -> ", e
        cfg.logger.exception(e)
        # raise
    finally:
        print "Waiting for throughput server to finish.."
        from throughput import ThroughputTestClient
        ThroughputTestClient(None).finish_server()
        tt_server.join()

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
