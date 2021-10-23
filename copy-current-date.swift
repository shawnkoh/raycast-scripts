#!/usr/bin/swift

// Required parameters:
// @raycast.schemaVersion 1
// @raycast.title Copy Current Date
// @raycast.mode silent
// @raycast.refreshTime 1d

// Optional parameters:
// @raycast.icon 🤖
// @raycast.packageName Current Date

// Documentation:
// @raycast.author Shawn Koh
// @raycast.authorURL https://shawnkoh.sg

import AppKit

let formatter = ISO8601DateFormatter()
formatter.formatOptions = .withFullDate
let date = formatter.string(from: Date())
NSPasteboard.general.clearContents()
NSPasteboard.general.writeObjects([date as NSPasteboardWriting])
print(date)
