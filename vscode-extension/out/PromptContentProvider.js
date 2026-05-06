"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.PromptContentProvider = exports.SCHEME = void 0;
exports.makeUri = makeUri;
const vscode = __importStar(require("vscode"));
const cli_1 = require("./cli");
exports.SCHEME = "promptvc";
class PromptContentProvider {
    provideTextDocumentContent(uri) {
        // URI: promptvc://prompt-name/vN
        const [name, versionStr] = uri.path.replace(/^\//, "").split("/");
        const versionNum = parseInt(versionStr.replace("v", ""), 10);
        const detail = (0, cli_1.showVersion)(name, versionNum);
        return detail
            ? detail.content
            : `Could not load ${name} v${versionNum}`;
    }
}
exports.PromptContentProvider = PromptContentProvider;
function makeUri(promptName, versionNum) {
    return vscode.Uri.parse(`${exports.SCHEME}://${promptName}/v${versionNum}?t=${Date.now()}`);
}
//# sourceMappingURL=PromptContentProvider.js.map