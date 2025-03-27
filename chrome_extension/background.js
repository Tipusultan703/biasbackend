// Create Context Menu on Install
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "analyzeBias",
    title: "Analyze Bias in News",
    contexts: ["selection"] // Show only when text is selected
  });
});

// Handle Right-Click Event
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "analyzeBias" && info.selectionText) {
    chrome.storage.local.set({ selectedText: info.selectionText }, () => {
      chrome.action.openPopup(); // Open popup automatically
    });
  }
});


  


