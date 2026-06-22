type ClipboardWriter = Pick<Clipboard, "writeText">;

export async function copyTextWithFeedback(
  value: string,
  successMessage: string,
  onCopied: (message: string) => void,
  clipboard: ClipboardWriter = navigator.clipboard,
) {
  try {
    await clipboard.writeText(value);
    onCopied(successMessage);
  } catch {
    onCopied("Could not copy request sample.");
  }
}
