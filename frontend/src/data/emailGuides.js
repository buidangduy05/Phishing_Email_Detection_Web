const emailGuides = [
  {
    id: "gmail",
    name: "Gmail",
    label: "Google",
    icon: "G",
    steps: [
      "Open the message you want to check.",
      "Select the three-dot More menu next to Reply.",
      'Choose "Download message" to save the email as an .eml file.',
      "Return here and upload the downloaded file.",
    ],
  },
  {
    id: "yahoo",
    name: "Yahoo Mail",
    label: "Yahoo",
    icon: "Y",
    steps: [
      "Open the email in Yahoo Mail.",
      "Select the More options menu in the message toolbar.",
      'Choose "View raw message" or "View message source."',
      "Save the message source as a .eml file, then upload it here.",
    ],
  },
  {
    id: "thunderbird",
    name: "Thunderbird",
    label: "Mozilla",
    icon: "T",
    steps: [
      "Select the message in your inbox.",
      "Open the message menu, or right-click the message.",
      'Choose "Save As..." and keep the .eml file format.',
      "Upload the saved file to start the analysis.",
    ],
  },
  {
    id: "outlook",
    name: "Outlook",
    label: "Microsoft",
    icon: "O",
    steps: [
      "Open the message in Outlook on the web or desktop.",
      "Open the message's More actions menu.",
      'Choose "Download" or "Save as" and select the .eml format if offered.',
      "If your Outlook version only offers .msg, use another mail app to export as .eml.",
    ],
  },
];

export default emailGuides;
