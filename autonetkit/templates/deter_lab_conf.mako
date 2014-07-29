### to be processed by gendeter.py ###
[Lab]
LAB_DESCRIPTION="${topology.description}"
LAB_VERSION="${version_banner}"
LAB_AUTHOR="${topology.author}"
LAB_EMAIL="${topology.email}"
LAB_WEB="${topology.web}"

[machines]
machines=${topology.machines}

[Net]
% for config_item in topology.config_items:
${config_item.device},${config_item.interface}=${config_item.ip},${config_item.cd}
%endfor
