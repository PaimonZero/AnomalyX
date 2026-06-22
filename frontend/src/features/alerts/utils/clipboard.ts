type ClipboardWriter = Pick<Clipboard, "writeText">;

export async function copyTextToClipboard(
  value: string,
  clipboard: ClipboardWriter = navigator.clipboard,
) {
  try {
    await clipboard.writeText(value);
    return true;
  } catch {
    return false;
  }
}
