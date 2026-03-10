import debloat_components.debloat_execute_external_scripts as external_scripts


def main(config_path=None):
    external_scripts.run_winutil(config_path)


if __name__ == "__main__":
    main()
