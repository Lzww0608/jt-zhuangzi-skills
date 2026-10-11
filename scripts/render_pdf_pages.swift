// macOS: swift -module-cache-path /private/tmp/jt-swift-cache scripts/render_pdf_pages.swift INPUT.pdf OUTPUT_DIR [START] [END]
// Render original pages for visual proofreading; no change to source PDF.
import Foundation
import PDFKit
import AppKit

let args = CommandLine.arguments
guard args.count >= 3, let document = PDFDocument(url: URL(fileURLWithPath: args[1])) else {
    fatalError("Usage: render_pdf_pages.swift INPUT.pdf OUTPUT_DIR [START] [END]")
}
let start = args.count > 3 ? Int(args[3])! : 1
let end = args.count > 4 ? Int(args[4])! : document.pageCount
try FileManager.default.createDirectory(atPath: args[2], withIntermediateDirectories: true)
for number in start...min(end, document.pageCount) {
    try autoreleasepool {
        let page = document.page(at: number - 1)!
        let bounds = page.bounds(for: .mediaBox)
        let scale: CGFloat = 2400 / max(bounds.width, bounds.height)
        let width = Int(bounds.width * scale), height = Int(bounds.height * scale)
        let ctx = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8,
                            bytesPerRow: width * 4, space: CGColorSpaceCreateDeviceRGB(),
                            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
        ctx.setFillColor(NSColor.white.cgColor)
        ctx.fill(CGRect(x: 0, y: 0, width: width, height: height))
        ctx.scaleBy(x: scale, y: scale)
        ctx.translateBy(x: -bounds.minX, y: -bounds.minY)
        page.draw(with: .mediaBox, to: ctx)
        let bitmap = NSBitmapImageRep(cgImage: ctx.makeImage()!)
        let png = bitmap.representation(using: .png, properties: [:])!
        let filename = String(format: "p%04d.png", number)
        try png.write(to: URL(fileURLWithPath: args[2]).appendingPathComponent(filename))
    }
}
print("Rendered \(start)-\(min(end, document.pageCount)) to \(args[2])")
