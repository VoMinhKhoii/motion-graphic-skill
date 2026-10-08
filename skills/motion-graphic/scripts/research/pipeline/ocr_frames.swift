// ocr_frames.swift: read the text in images with macOS Vision and print one JSON line per image.
//
// Build:  swiftc -O ocr_frames.swift -o ocr_frames        (text_frames.py does this on first use)
// Usage:  ocr_frames [--fast] <image> [<image> ...]
//         ls frames/*.jpg | ocr_frames [--fast]            (paths on stdin, one per line, when none are given)
//
// Each line: {"image": path, "w": px, "h": px,
//             "lines": [{"text": str, "conf": 0..1, "box": [x, y, w, h]}]}
// box is normalised to the image (0..1) with the origin at the TOP-left, so box[3] * h is the line's pixel
// height (ascender to descender, roughly 1.4x the cap height). --fast trades accuracy for about 3x speed.
// macOS 10.15+; automatic language detection on macOS 13+.
import AppKit
import Foundation
import Vision

var fast = false
var paths: [String] = []
for a in CommandLine.arguments.dropFirst() {
  if a == "--fast" { fast = true } else { paths.append(a) }
}
if paths.isEmpty {
  while let line = readLine() {
    let p = line.trimmingCharacters(in: .whitespaces)
    if !p.isEmpty { paths.append(p) }
  }
}

func emit(_ obj: [String: Any]) {
  if let data = try? JSONSerialization.data(withJSONObject: obj, options: []), let s = String(data: data, encoding: .utf8) {
    print(s)
  }
}

for path in paths {
  guard let img = NSImage(contentsOf: URL(fileURLWithPath: path)),
    let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil)
  else {
    emit(["image": path, "error": "unreadable"])
    continue
  }
  let req = VNRecognizeTextRequest()
  req.recognitionLevel = fast ? .fast : .accurate
  req.usesLanguageCorrection = !fast
  if #available(macOS 13.0, *) { req.automaticallyDetectsLanguage = true }
  do {
    try VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
  } catch {
    emit(["image": path, "error": "\(error)"])
    continue
  }
  var lines: [[String: Any]] = []
  for obs in req.results ?? [] {
    guard let cand = obs.topCandidates(1).first else { continue }
    let b = obs.boundingBox
    let box = [b.minX, 1 - b.maxY, b.width, b.height].map { (Double($0) * 10000).rounded() / 10000 }
    lines.append(["text": cand.string, "conf": (Double(cand.confidence) * 100).rounded() / 100, "box": box])
  }
  emit(["image": path, "w": cg.width, "h": cg.height, "lines": lines])
}
