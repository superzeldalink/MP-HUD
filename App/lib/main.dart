
import 'package:flutter/material.dart';
import 'package:mp_hud/Settings/SelectBondedDevicePage.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: SelectBondedDevicePage(),
    );
  }
}

// class MyApp extends StatelessWidget {
//   const MyApp({Key? key}) : super(key: key);

//   int BitToByte(List<int> num) {
//     int result = 0;
//     for (int i = 0; i < 8; ++i) {
//       result |= ((num[i] & 1) << (7 - i));
//     }

//     return result;
//   }

//   @override
//   Widget build(BuildContext context) {
//     return MaterialApp(
//       home: Scaffold(
//         appBar: AppBar(
//           title: const Text("Image test"),
//         ),
//         body: Container(
//           child: TextButton(
//             onPressed: () async {
//               final ImagePicker _picker = ImagePicker();
//               final XFile? file =
//                   await _picker.pickImage(source: ImageSource.gallery);
//               final image = decodeImage(File(file!.path).readAsBytesSync());

//               int width = image!.width;
//               int height = image.height;

//               List<int> binImageArray = [];

//               int newRowSizeInBits =
//                   ((1 * image.width * 1.0 + 31) / 32).floor() * 4 * 8;

//               for (int i = 0; i < height; i++) {
//                 int j;
//                 for (j = 0; j < width; j++) {
//                   int color = image.getPixel(j,i);
//                   int r = color & 0xFF;
//                   int b = (color >> 8) & 0xFF;
//                   int g = (color >> 16) & 0xFF;

//                   double grayscale = (0.3 * r) + (0.59 * g) + (0.11 * b);
//                   int bit = grayscale > 60 ? 1 : 0;

//                   binImageArray.add(bit);
//                 }
//                 for (int k = j; k < newRowSizeInBits; k++) {
//                   // Set all 0 for padding
//                   binImageArray.add(0);
//                 }
//               }

//               print("$width $height ${binImageArray.length}");

//               String data = "";
//               List<int> dataInt = [];
//               int dataSize = (newRowSizeInBits * height / 8).floor();
//               for (int i = 0; i < dataSize; i++) {
//                 // For every 8 bits, pack into a byte, then store it
//                 List<int> byte = [];
//                 for (int j = 0; j < 8; j++) {
//                   byte.add(binImageArray[8 * i + j]);
//                 }
//                 data += "${BitToByte(byte)},";
//                 dataInt.add(BitToByte(byte));
//               }
//               print("${dataInt.length}");
//               log(data);
//               print(BitToByte([0,1,1,0,0,0,0,0]).toString());
//             },
//             child: Text("TEST!"),
//           ),
//         ),
//       ),
//     );
//   }
// }
