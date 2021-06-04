#include "common/common.h"
#include "common/string_utils.h"

#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>

int clientValidateInput(int argc, char **argv) {

	if (argc != 5) {
        commonDebugStep("ERROR: Invalid argc!\n");
		return 0;
    }

	const char *portStr = argv[2];
	if (!stringValidateNumericString(portStr, strlen(portStr))) {
		commonDebugStep("ERROR: Invalid Port!\n");
		return 0;
	}

	const char *msg = argv[3];
	if (!stringValidateLCaseString(msg, strlen(msg))) {
		commonDebugStep("ERROR: Invalid Text!\n");
		return 0;
	}

	const char *cipherKeyStr = argv[4];
	if (!stringValidateNumericString(cipherKeyStr, strlen(cipherKeyStr))) {
		commonDebugStep("ERROR: Invalid Cipher Key!\n");
		return 0;
	}

	return 1;
}

int clientParseAddress(const char *addrStr, const char *portstr, struct sockaddr_storage *addr) {
    
    // Valida parametros
    if (addrStr == NULL || portstr == NULL) {
        return 0;
    }

    // Converte string da porta para numero da porta (em network byte order)
    uint16_t port = (uint16_t)atoi(portstr); // unsigned short
    if (port == 0) {
        return 0;
    }
    port = htons(port); // host to network short

    // Trata ipv4
    struct in_addr addrNumber4;
	int is_ipv4 = inet_pton(AF_INET, addrStr, &addrNumber4);
	if (!is_ipv4) {
		return 0;
	}

    struct sockaddr_in *addr4 = (struct sockaddr_in *)addr;
    addr4->sin_family = AF_INET;
    addr4->sin_port = port;
    addr4->sin_addr = addrNumber4;

    return 1;
}
