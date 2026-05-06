import * as vscode from "vscode";
import { showVersion } from "./cli";

export const SCHEME = "promptvc";

export class PromptContentProvider
  implements vscode.TextDocumentContentProvider
{
  provideTextDocumentContent(uri: vscode.Uri): string {
    // URI: promptvc://prompt-name/vN
    const [name, versionStr] = uri.path.replace(/^\//, "").split("/");
    const versionNum = parseInt(versionStr.replace("v", ""), 10);
    const detail = showVersion(name, versionNum);
    return detail
      ? detail.content
      : `Could not load ${name} v${versionNum}`;
  }
}

export function makeUri(promptName: string, versionNum: number): vscode.Uri {
  return vscode.Uri.parse(
    `${SCHEME}://${promptName}/v${versionNum}?t=${Date.now()}`
  );
}
