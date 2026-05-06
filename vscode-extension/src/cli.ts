import { spawnSync } from "child_process";
import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";

export interface PromptSummary {
  name: string;
  description: string | null;
  version_count: number;
  latest_version: number | null;
  last_env: string | null;
  updated_at: string;
}

export interface VersionSummary {
  version_num: number;
  message: string;
  author: string | null;
  environment: string;
  token_count: number | null;
  created_at: string;
  tags: string | null;
}

export interface VersionDetail {
  version_num: number;
  content: string;
  message: string;
  environment: string;
  token_count: number | null;
  model_hint: string | null;
  author: string | null;
  content_hash: string;
  created_at: string;
}

function cwd(): string {
  return vscode.workspace.workspaceFolders?.[0].uri.fsPath ?? process.cwd();
}

function run(args: string[]): { ok: boolean; stdout: string; stderr: string } {
  const result = spawnSync("promptvc", args, {
    cwd: cwd(),
    encoding: "utf8",
    timeout: 10_000,
  });
  return {
    ok: result.status === 0,
    stdout: result.stdout ?? "",
    stderr: result.stderr ?? "",
  };
}

export function isInitialized(): boolean {
  let dir = cwd();
  while (true) {
    if (fs.existsSync(path.join(dir, ".promptvc", "store.db"))) {
      return true;
    }
    const parent = path.dirname(dir);
    if (parent === dir) {
      break;
    }
    dir = parent;
  }
  return false;
}

export function listPrompts(): PromptSummary[] {
  const r = run(["list", "--json"]);
  if (!r.ok) {
    return [];
  }
  try {
    return JSON.parse(r.stdout) as PromptSummary[];
  } catch {
    return [];
  }
}

export function logVersions(name: string): VersionSummary[] {
  const r = run(["log", name, "--json"]);
  if (!r.ok) {
    return [];
  }
  try {
    return JSON.parse(r.stdout) as VersionSummary[];
  } catch {
    return [];
  }
}

export function showVersion(name: string, versionNum: number): VersionDetail | null {
  const r = run(["show", name, "--version", String(versionNum), "--json"]);
  if (!r.ok) {
    return null;
  }
  try {
    return JSON.parse(r.stdout) as VersionDetail;
  } catch {
    return null;
  }
}

export function runInit(): { ok: boolean; message: string } {
  const r = run(["init"]);
  return { ok: r.ok, message: r.stdout || r.stderr };
}

export function runAdd(name: string, filePath: string): { ok: boolean; message: string } {
  const r = run(["add", name, "--file", filePath]);
  return { ok: r.ok, message: r.stdout || r.stderr };
}

export function runCommit(
  name: string,
  message: string
): { ok: boolean; message: string } {
  const r = run(["commit", name, "-m", message]);
  return { ok: r.ok, message: r.stdout || r.stderr };
}

export function runRollback(
  name: string,
  versionNum: number
): { ok: boolean; message: string } {
  const r = run(["rollback", name, "--version", String(versionNum)]);
  return { ok: r.ok, message: r.stdout || r.stderr };
}
