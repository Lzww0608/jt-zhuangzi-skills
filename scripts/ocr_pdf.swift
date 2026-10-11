// macOS: swift scripts/ocr_pdf.swift INPUT.pdf OUTPUT.jsonl [START] [END]
// Local OCR only. Page numbers are 1-based PDF page numbers.
import Foundation
import PDFKit
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count >= 3, let document = PDFDocument(url: URL(fileURLWithPath: args[1])) else {
    fatalError("Usage: ocr_pdf.swift INPUT.pdf OUTPUT.jsonl [START] [END]")
}
let start = args.count > 3 ? Int(args[3])! : 1
let end = args.count > 4 ? Int(args[4])! : document.pageCount
FileManager.default.createFile(atPath: args[2], contents: nil)
let output = try FileHandle(forWritingTo: URL(fileURLWithPath: args[2]))
for number in start...min(end, document.pageCount) {
    try autoreleasepool {
        guard let page = document.page(at: number - 1) else { fatalError("Missing page") }
        let bounds = page.bounds(for: .mediaBox)
        let scale: CGFloat = 2400 / max(bounds.width, bounds.height)
        let width = Int(bounds.width * scale), height = Int(bounds.height * scale)
        guard let ctx = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8,
                                  bytesPerRow: width * 4, space: CGColorSpaceCreateDeviceRGB(),
                                  bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { fatalError("Context") }
        ctx.setFillColor(NSColor.white.cgColor)
        ctx.fill(CGRect(x: 0, y: 0, width: width, height: height))
        ctx.scaleBy(x: scale, y: scale)
        ctx.translateBy(x: -bounds.minX, y: -bounds.minY)
        page.draw(with: .mediaBox, to: ctx)
        guard let cgImage = ctx.makeImage() else { fatalError("Image") }
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.recognitionLanguages = ["zh-Hant", "zh-Hans", "en-US"]
        request.usesLanguageCorrection = true
        do {
            try VNImageRequestHandler(cgImage: cgImage, options: [:]).perform([request])
        } catch {
            fputs("OCR page \(number) failed: \(error as NSError)\n", stderr)
            exit(2)
        }
        let observations = (request.results ?? []).sorted {
            if abs($0.boundingBox.midY - $1.boundingBox.midY) > 0.006 {
                return $0.boundingBox.midY > $1.boundingBox.midY
            }
            return $0.boundingBox.minX < $1.boundingBox.minX
        }
        let lines: [[String: Any]] = observations.compactMap { o in
            guard let c = o.topCandidates(1).first else { return nil }
            return ["text": c.string, "confidence": c.confidence,
                    "bbox": [o.boundingBox.minX, o.boundingBox.minY, o.boundingBox.width, o.boundingBox.height]]
        }
        let record: [String: Any] = ["page": number, "text": lines.map { $0["text"] as! String }.joined(separator: "\n"),
                                     "method": "Apple Vision accurate zh-Hant/zh-Hans/en-US, 2400px", "lines": lines]
        let data = try JSONSerialization.data(withJSONObject: record, options: [.sortedKeys])
        try output.write(contentsOf: data)
        try output.write(contentsOf: Data("\n".utf8))
        print("OCR page \(number)/\(document.pageCount): \(lines.count) lines")
        fflush(stdout)
    }
}
try output.close()
