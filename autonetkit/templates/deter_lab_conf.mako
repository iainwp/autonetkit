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
% for ci in topology.config_items:
${ci.device},${ci.interface}=${ci.ip},${ci.cd},${ci.mask}
%endfor
