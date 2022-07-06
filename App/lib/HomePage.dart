import 'dart:async';
import 'dart:developer';
import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';

import 'package:image/image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';
import 'package:image_picker/image_picker.dart';

import 'package:mp_hud/Settings/SettingsPage.dart';

class HomePage extends StatefulWidget {
  final BluetoothDevice server;
  const HomePage({Key? key, required this.server}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _Message {
  int whom;
  String text;

  _Message(this.whom, this.text);
}

class _HomePageState extends State<HomePage> {
  late Widget container;

  static final clientID = 0;
  BluetoothConnection? connection;

  List<_Message> messages = List<_Message>.empty(growable: true);
  String _messageBuffer = '';

  final TextEditingController textEditingController =
      new TextEditingController();
  final ScrollController listScrollController = new ScrollController();

  bool isConnecting = true;
  bool get isConnected => (connection?.isConnected ?? false);

  bool isDisconnecting = false;

  List<String> cmdList = List<String>.empty(growable: true);
  bool sent = false;
  bool executing = false;

  @override
  void initState() {
    super.initState();
    cmdList = [];

    BluetoothConnection.toAddress(widget.server.address).then((_connection) {
      print('Connected to the device');
      connection = _connection;
      setState(() {
        isConnecting = false;
        isDisconnecting = false;
      });

      connection!.input!.listen(_onDataReceived).onDone(() {
        // Example: Detect which side closed the connection
        // There should be `isDisconnecting` flag to show are we are (locally)
        // in middle of disconnecting process, should be set before calling
        // `dispose`, `finish` or `close`, which all causes to disconnect.
        // If we except the disconnection, `onDone` should be fired as result.
        // If we didn't except this (no flag set), it means closing by remote.
        if (isDisconnecting) {
          print('Disconnecting locally!');
        } else {
          print('Disconnected remotely!');
        }
        if (this.mounted) {
          setState(() {});
        }
      });
    }).catchError((error) {
      print('Cannot connect, exception occured');
      print(error);
    });
  }

  @override
  void dispose() {
    // Avoid memory leak (`setState` after dispose) and disconnect
    if (isConnected) {
      isDisconnecting = true;
      connection?.dispose();
      connection = null;
    }

    super.dispose();
  }

  ListTile Page(String title, IconData icon, Widget page) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      onTap: () {
        setState(
          () {
            Navigator.pop(context);
            container = page;
          },
        );
      },
    );
  }

  void _onDataReceived(Uint8List data) async {
    // Allocate buffer for parsed data
    int backspacesCounter = 0;
    data.forEach((byte) {
      if (byte == 8 || byte == 127) {
        backspacesCounter++;
      }
    });
    Uint8List buffer = Uint8List(data.length - backspacesCounter);
    int bufferIndex = buffer.length;

    // Apply backspace control character
    backspacesCounter = 0;
    for (int i = data.length - 1; i >= 0; i--) {
      if (data[i] == 8 || data[i] == 127) {
        backspacesCounter++;
      } else {
        if (backspacesCounter > 0) {
          backspacesCounter--;
        } else {
          buffer[--bufferIndex] = data[i];
        }
      }
    }

    // Create message if there is new line character
    String dataString = String.fromCharCodes(buffer);
    int index = buffer.indexOf(13);

    if (~index != 0) {
      String mess = backspacesCounter > 0
          ? _messageBuffer.substring(
              0, _messageBuffer.length - backspacesCounter)
          : _messageBuffer + dataString.substring(0, index);

      mess = mess.trim();
      print(mess);
      _messageBuffer = dataString.substring(index);

      if (mess == "E") {
        const snackBar = SnackBar(
          content: Text('Error! Try again!'),
        );
        ScaffoldMessenger.of(context).showSnackBar(snackBar);
      }
    } else {
      _messageBuffer = (backspacesCounter > 0
          ? _messageBuffer.substring(
              0, _messageBuffer.length - backspacesCounter)
          : _messageBuffer + dataString);
    }
  }

  void sendBytes(List<int> bytes) async {
    connection!.output.add(Uint8List.fromList(bytes));
    await connection!.output.allSent;
  }

  void sendText(String text) {
    List<int> bytes = [4, 12, 0, 0] + utf8.encode(text);
    sendBytes(bytes);
  }

  int BitToByte(List<int> num) {
    int result = 0;
    for (int i = 0; i < 8; ++i) {
      result |= ((num[i] & 1) << (7 - i));
    }

    return result;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("MP-HUD"),
      ),
      drawer: Drawer(
        child: ListView(
          // Important: Remove any padding from the ListView.
          padding: EdgeInsets.zero,
          children: const [
            DrawerHeader(
              decoration: BoxDecoration(
                color: Colors.blue,
              ),
              child: Text('MP-HUD'),
            ),
            // Page("Home", Icons.home, const HomePage()),
            // Page("Settings", Icons.settings, SettingsPage()),
          ],
        ),
      ),
      body: isConnected
          ? SingleChildScrollView(
              child: Column(
                children: [
                  TextField(
                    decoration: const InputDecoration(
                      hintText: 'Enter a text',
                    ),
                    onChanged: (string) async {
                      sendText(string);
                    },
                  ),
                  TextButton(
                    child: const Text("Clear screen"),
                    onPressed: () async {
                      sendBytes([0]);
                    },
                  ),
                  TextButton(
                    child: const Text("Home"),
                    onPressed: () async {
                      sendBytes([0]);

                      await Future.delayed(const Duration(milliseconds: 50));

                      DateTime now = DateTime.now();
                      String year = now.year.toString();
                      var bytes = [
                        int.parse(year.substring(year.length - 2)),
                        now.month,
                        now.day,
                        now.weekday,
                        now.hour,
                        now.minute,
                        now.second
                      ];
                      sendBytes(bytes);

                      await Future.delayed(const Duration(milliseconds: 50));

                      sendBytes([2]);
                    },
                  ),
                  TextButton(
                    onPressed: () async {
                      setState(() {
                        executing = true;
                      });
                      final ImagePicker _picker = ImagePicker();
                      final XFile? file =
                          await _picker.pickImage(source: ImageSource.gallery);
                      var image =
                          decodeImage(File(file!.path).readAsBytesSync());

                      int width = image!.width;
                      int height = image.height;

                      if (width > 128 || height > 64) {
                        if (width / height <= 2) {
                          image = copyResize(image, height: 64);
                        } else {
                          image = copyResize(image, width: 128);
                        }
                      }

                      width = image.width;
                      height = image.height;

                      List<int> binImageArray = [];

                      int newRowSizeInBits =
                          ((1 * image.width * 1.0 + 31) / 32).floor() * 4 * 8;

                      for (int i = 0; i < height; i++) {
                        int j;
                        for (j = 0; j < width; j++) {
                          int color = image.getPixel(j, i);
                          int r = color & 0xFF;
                          int b = (color >> 8) & 0xFF;
                          int g = (color >> 16) & 0xFF;

                          double grayscale =
                              (0.3 * r) + (0.59 * g) + (0.11 * b);
                          int bit = grayscale > 127 ? 1 : 0;

                          binImageArray.add(bit);
                        }
                        for (int k = j; k < newRowSizeInBits; k++) {
                          // Set all 0 for padding
                          binImageArray.add(0);
                        }
                      }

                      List<int> data = [];
                      int dataSize = (newRowSizeInBits * height / 8).floor();
                      for (int i = 0; i < dataSize; i++) {
                        // For every 8 bits, pack into a byte, then store it
                        List<int> byte = [];
                        for (int j = 0; j < 8; j++) {
                          byte.add(binImageArray[8 * i + j]);
                        }
                        data.add(BitToByte(byte));
                      }
                      var compressedData = zlib.encode(data);

                      List<int> bytes =
                          [3, width, height, 0, 0] + compressedData;
                      sendBytes(bytes);
                    },
                    child: const Text("Image"),
                  ),
                  TextButton(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) {
                            return MyScript(
                              sendText: sendText,
                            );
                          },
                        ),
                      );
                    },
                    child: const Text("MY SCRIPT"),
                  ),
                ],
              ),
            )
          : Container(
              child: Center(
                  child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: const [
                  CircularProgressIndicator(),
                  SizedBox(
                    width: 10.0,
                  ),
                  Text("Connecting, please wait..."),
                ],
              )),
            ),
    );
  }
}

class MyScript extends StatefulWidget {
  const MyScript({Key? key, required this.sendText}) : super(key: key);

  final Function sendText;
  @override
  State<MyScript> createState() => _MyScriptState();
}

int currentScript = 0;
var script = [
  [
    "Slide 1",
    "Briefly introduce our project's target, object of use, unique point (innovative idea)."
  ],
  ["Slide 1", "Our project is about portable and attached devices in glasses."],
  ["Slide 1", "- Following basic tasks \n - Navigating \n - Parameters."],
  [
    "Slide 1",
    "After round 1, thanks to the comment of judges, and some random volunteer testers,"
  ],
  ["Slide 1", "we have modified user oriented and design of model"],
  [
    "Slide 1",
    "To be more specific, our initial aim is displaying text, measuring the parameters"
  ],
  [
    "Slide 1",
    "driver's convenience for navigating and displaying the Google map direction guide."
  ],
  [
    "Slide 1",
    "also changed the priority of developing our mobile app to real-time displaying text"
  ],
  [
    "Slide 1",
    "text displaying from voice recognizing with mic of phone for disabled-people"
  ],
  ["Slide 1", "and keeping Google Map Guide"],
  ["Slide 5", "Slide 5: Compared the old and new design"],
  [
    "Slide 1",
    "As you can see, this is the design we have introduced in round 1"
  ],
  [
    "Slide 1",
    "you can see that the arrangement of all components aligned in 1 line"
  ],
  [
    "Slide 1",
    "and made the length and the width of the device reach to 15 cm and 3 cm"
  ],
  [
    "Slide 1",
    "respectively, however after we had chosen particularly all the components in reality,"
  ],
  [
    "Slide 1",
    "we have succeeded in reducing the length and the width to 11 cm and 2.2 cm "
  ],
  ["Slide 1", "as you can see the picture toward the left side of me"],
  ["Slide 1", "It is less weight and more succinct compared to the old."],
  ["Slide 6-7", "Slide 6+7: Working Principle"],
  ["Slide 6-7", "After that, we adjust the angle of the display screen "],
  ["Slide 6-7", "compared to the view of the eye."],
  ["Slide 6-7", "Now, we come to the optical working principle of the device"],
  ["Slide 6-7", "As we use the magnifying glasses"],
  ["Slide 6-7", "it give us the virtual, erect(reverse) and larger object"],
  ["Slide 6-7", "but what we expect is virtual, inverted"],
  ["Slide 6-7", "and larger image in screen, so that we decided to put"],
  ["Slide 6-7", "in turn base on the new arrangement"],
];

class _MyScriptState extends State<MyScript> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Script')),
      body: Column(
        children: [
          Flexible(
            child: ListView.builder(
              itemCount: script.length,
              itemBuilder: (BuildContext context, int index) {
                return ListTile(
                  title: Text(script[index][0]),
                  subtitle: Text(script[index][1]),
                  selected: currentScript == index ? true : false,
                  onTap: () async {
                    setState(() {
                      currentScript = index;
                    });
                    widget.sendText(script[index][1]);
                  },
                );
              },
            ),
          ),
          Container(
            height: 100,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Expanded(
                  child: TextButton(
                    onPressed: currentScript == 0
                        ? null
                        : () {
                            setState(() {
                              currentScript--;
                              widget.sendText(script[currentScript][1]);
                            });
                          },
                    child: const Text("Back"),
                  ),
                ),
                Expanded(
                  child: TextButton(
                    onPressed: currentScript == script.length - 1
                        ? null
                        : () {
                            setState(() {
                              currentScript++;
                              widget.sendText(script[currentScript][1]);
                            });
                          },
                    child: const Text("Next"),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
