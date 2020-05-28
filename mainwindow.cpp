#include "mainwindow.h"
#include "ui_mainwindow.h"

/********************************************************************************
* Create a text file suitable to sending to a Wearable from an Intel hex file   *
*********************************************************************************/
MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{

    ui->setupUi(this);
    highestAddress = 0;

}

MainWindow::~MainWindow()
{
    delete ui;
}

/********************************************************************************
* User selects an existing intel hex file name whose name is used to create the *
* name of the text file that is used to program the Wearable                    *
* Filenames come from and go to line text edit widgets in the main window       *
*********************************************************************************/
void MainWindow::selectHexFile()
{

    QString previousDirectory;
    QString hexFileName;
    int i;
    int dirLen;
    int charsToRemove;
    QString tempStr;
    QString FullNameHolder;

    previousDirectory = selectPreviousDirectory();

    hexFileName = QFileDialog::getOpenFileName(this,"Select Intel Hex File to load.",previousDirectory,".hex (*.hex)");
    ui->fileNameLineEdit->setText(hexFileName);

    tempStr = hexFileName;
    FullNameHolder = hexFileName;
    i = tempStr.lastIndexOf("/");
    dirLen = hexFileName.length();
    charsToRemove = dirLen - i;
    hexFileDirectory = hexFileName.remove(i,charsToRemove);
    targetFileName = tempStr.mid(++i);
    targetFileName += ".txt";
    ui->nameOfFileLineEdit->setText(targetFileName);

    highestAddress = 0;

    fillArray();
    createTextFile();


}



/****************************************************************************************************
 * This function keeps track of what directory the previously selected hex file to encrypt was      *
 * stored so it keeps the number of clicks to a minimum. It stores a line in a file that's used     *
 *  for the program to start at this directory when it's picking the unencrypted file next time.    *
 * Thus it is remembered even when the program is shut down. The file is a .txt file and is stored  *
 * * in the direcotry from which the program is run.                                                *
 * This function returns the value read from the config file                                        *
 ***************************************************************************************************/
QString MainWindow::selectPreviousDirectory(void)
{

    QString exectDir;
    QString retVal;
    QString s;

    exectDir = QDir::currentPath(); // The file that the previously used directory is stored in is in the executable's part...
    QFile file( exectDir + "/last_dir.txt" ); // ...and is called last_dir.txt

    retVal = QDir::homePath();  // Default return value in case the file is lost, deleted or it's the first time the program has been run

    if (file.open(QIODevice::ReadOnly))
    {
        QTextStream	OpenStream (&file);
        while ( !OpenStream.atEnd() )
        {
            s=OpenStream.readLine();		// Read a line as a string and put it in s
            if (s.contains("last_directory="))
                retVal = s.section('=',1);
        }

        file.close();
    }

    return retVal;

}


/****************************************************************************************************
 * The program keeps track of what directory the previously selected hex file to encrypt was stored *
 * in so that it keeps the number of clicks to a minimum. It stores a line in a file that is used   *
 * for the program to start at this directory when it's picking the unencrypted file next time.     *
 * Thus it is remembered even when the program is shut down. The file is a .txt file and is stored  *
 * * in the direcotry from which the program is run.                                                *
 * This function stores the current directory with the selected file in it, into the config file    *
 ***************************************************************************************************/
void MainWindow::WritePreviousDirectory(QString prevDir)
{

    QString execDir;
    execDir = QDir::currentPath();
    QFile file( execDir + "/last_dir.txt" );
    QString lineToWrite;

    if (file.open(QIODevice::WriteOnly))
    {
        QTextStream stream( &file );
        lineToWrite = "last_directory=" + prevDir + "/";
        stream << lineToWrite << "\n";	// And a new line
        file.close();
    }


}


/****************************************************************************************************
 * createTextFile() creates a file suitable for sownloading a programming the wearable.             *
 * It creates three basic message types:                                                            *
 * Erase boundaries. Line starts with $                                                             *
 * Program Page. Starts with *                                                                      *
 * Image CRC. Starts with #                                                                         *
 * The file created is an easy-to-read ASCII file that is dpwnload to the wearable over HTTPS       *
 ***************************************************************************************************/
void MainWindow::createTextFile(void)
{

    quint32 i;
    QString hexFileName;
    QString newFileName;
    QString newLine;
    CRC crcInst;
    QString imageCRCString;
    QString eraseLineString;


    i = 0;
    firstPage = true;

// First open the selected existing hex file
    QFile f2 ( ui->fileNameLineEdit->text());
    f2.open ( QIODevice::ReadOnly );
    QTextStream	OpenStream ( &f2 );

// Next set up the new file to be written
    newFileName = hexFileDirectory + "/" +  ui->nameOfFileLineEdit->text();
    QFile file(newFileName);
    QTextStream stream( &file );

    eraseLineString = createEraseSection(0);

    stream << eraseLineString << "\n";

    if ( file.open( QIODevice::WriteOnly ) )
    {
        while (i<MEMORY_ARRAY_SIZE)
        {
            if (pageBoundary(i) == true)
            {
                newLine = createPage(i);
                if (newLine != "")
                {
                    stream << newLine << "\n";
                }
                i += SAM4C_PAGE_SIZE;
            }
            else
            {
                i++;
            }
        }

    }

    ui->textEdit->appendPlainText("Highest address is " + QString::number(highestAddress,16));

    imageCRC.CRCInt = 0xFFFF;
    crcInst.GetCRC(&memoryArray[0],highestAddress,&imageCRC);
    ui->textEdit->appendPlainText("CRC for image is " + QString::number(imageCRC.CRCInt,16));

    imageCRCString = "# " + QString::number(lowestAddress,16) + " " + QString::number((highestAddress + MEMORY_OFFSET),16) + " " +  QString("%1").arg(imageCRC.CRCInt, 4, 16, QChar('0')) + " " + ETX;

    stream << imageCRCString << "\n";

}

/****************************************************************************************************
 * createEraseSection() creates a section in the programmable test file that tells the wearable     *
 * the range of addresses in flash that need erasing in preparation for repgoramming                *
 * Section is of type $ START_ADDRESS END_ADDRESS ETX Start and end address are seven bytes long    *
 * Passed the start address in the array created from the hex file                                  *
 * Returned string of what is to be written to the new file                                         *
 ***************************************************************************************************/
QString MainWindow::createEraseSection(uint32_t startAddress)
{

    quint32 i;
    QString retVal;
    bool dataInPage;
    bool firstLine;

    i = startAddress;

    firstLine = true;

    while (i<MEMORY_ARRAY_SIZE)
    {
        if (pageBoundary(i) == true)
        {
            dataInPage = detectDataInPage(i);
            if (dataInPage == true)
            {
                if (firstLine == true)
                {
                    lowestAddress = MEMORY_OFFSET + i;
                    firstLine = false;
                }
                else
                    highestAddress = MEMORY_OFFSET + i;

            }
            i += SAM4C_PAGE_SIZE;
        }
        else
        {
            i++;
        }
    }

    highestAddress += SAM4C_PAGE_SIZE;

    retVal = "$ " + QString::number(lowestAddress,16) + " " + QString::number((highestAddress),16) + " " + ETX;


    return retVal;
}

/****************************************************************************************************
 * detectDataInPage looks through a page of flash in the array previously created from the hex      *
 * file and if there is a non 0xFFFF value in it, returns true, indicating there is data in the     *
 * page that needs programming                                                                      *
 * Passed start address of page                                                                     *
 * Returned: true or flase                                                                          *
 ***************************************************************************************************/
bool MainWindow::detectDataInPage(quint32 startAddress)
{

    quint32 i;
    bool dataInPage;
    QString retVal;
    dataInPage = false;

    for (i=0; i<SAM4C_PAGE_SIZE; i++)
    {
        if (memoryArray[startAddress+i] != 0xFFFF)
        {
            dataInPage = true;
            i = SAM4C_PAGE_SIZE;
        }
    }

    return dataInPage;

}

/****************************************************************************************************
 * createPage takes [up to] 512 bytes of program memory, starting on a page boundary and creates    *
 * a packet of information                                                                          *
 * It is passed the start address of a page and returns a strong to be written to the new file      *
 ***************************************************************************************************/
QString MainWindow::createPage(uint32_t startAddress)
{

    QString retVal;
    quint16 i;
    quint8 j;
    bool dataInPage;
    quint32 dataStartAddress;
    quint16 numberOfDataBytesInPage;
    QString numberStr;
    CRC cc;
    CRCUnion calculatedCRC;

    dataInPage = false;
    dataStartAddress = 0;
    numberOfDataBytesInPage = 0;

    // First check whether there's actually any data in this page to program
    for (i=0; i<SAM4C_PAGE_SIZE; i++)
    {
        if (memoryArray[startAddress+i] != 0xFFFF)
        {
            dataInPage = true;
            dataStartAddress = (startAddress + MEMORY_OFFSET);
            numberOfDataBytesInPage = SAM4C_PAGE_SIZE;
            i = SAM4C_PAGE_SIZE;
        }
    }

    if (dataInPage == true)
    {
        if (firstPage == true)
        {
            lowestAddress = dataStartAddress;
            firstPage = false;
        }
        retVal = "* " + QString::number(dataStartAddress,16) + " " + QString::number(numberOfDataBytesInPage,16) + "\n";
        j = 0;
        for (i=0; i<SAM4C_PAGE_SIZE; i++)
        {
            numberStr = QString::number((memoryArray[startAddress + i] & 0xFF),16) + " ";
            if (memoryArray[startAddress + i] < 0x10)
                numberStr.prepend("0");
            retVal += numberStr;
            j++;
            if (j==16)
            {
                retVal += "\n";
                j = 0;
            }
        }
        highestAddress = i + startAddress;
        calculatedCRC = cc.getCRCFromString(retVal);

        numberStr = QString::number(calculatedCRC.CRCChar[1],16) + " ";
        if (calculatedCRC.CRCChar[1] < 0x10)
        {
            numberStr.prepend("0");
        }
        retVal += numberStr;

        numberStr = QString::number(calculatedCRC.CRCChar[0],16) + " ";
        if (calculatedCRC.CRCChar[0] < 0x10)
        {
            numberStr.prepend("0");
        }
        retVal += numberStr;

        retVal += ETX;
    }

    return retVal;

}


/****************************************************************************************************
 * Page boundaries are important because program memery is packaged into SAM4C_PAGE_SIZE "lines" of *
 * data to be sent to the wearable. Th-is simply tells us whether an address is on a boundary.      *
 ****************************************************************************************************/
bool MainWindow::pageBoundary(uint32_t arrayPosition)
{

    bool retVal;

    if ((arrayPosition % SAM4C_PAGE_SIZE) == 0)
    {
        retVal = true;
    }
    else
    {
        retVal = false;
    }
    return retVal;

}

/****************************************************************************************************
 * Return the path of the hex file select. Said file is in the edit box on the main screen          *
 ****************************************************************************************************/
QString MainWindow::returnHexPath(void)
{

    QString hexFileName;
    QString retVal;

    hexFileName = ui->fileNameLineEdit->text();
    QFile f2 (hexFileName);	// hexFileName is chosen by the user and is a global variable
    QFileInfo qFO(f2);
    retVal = qFO.absolutePath() + "/"; // Write to the file that keeps track of the previous directory, so we open in the correct dir next time

    return retVal;


}

/****************************************************************************************************
 * fillArray                                                                                        *
 * There is an array of the size of a single plane of flash in the SAM4C, but uses 16-bit variables *
 * * rather than the 8-bit size in the SAM itself.                                                  *
 *                                                                                                  *
 * This flash is filled with 0xFFFF and when a non-0xFF value is found in the SAM's hex file, its   *
 * value in the array is changed to be that value. This way, we know whether there is anything to   *
 * change in a page of SAM flash. Can scan through a page's worth of data and if there are any non  *
 * OxFFF values it is immediately obvious that there is data to program in that page                *
 * The program opens the Intel hex file keeps track of where it is in the SAM's address but removes *
 * the lowest address in the flash plane for storage in the array. So, as flash starts at 0x1000000`*
 * this value of 0x1000000 is subtracted from the address and used as the array's index             *
 ****************************************************************************************************/
void MainWindow::fillArray(void)
{

    int j;
    int l;
    int m;
    QString		s;
    quint16 LineArray[16];
    QString tempStr;
    int NumberOfBytes;
    int DataType;
    quint32 Address;
    quint16 memVal;
    quint32 lineNumber;
    quint32 Offset;
    QString hexFileName;
    quint32 addressToProgram;
    bool ok;


    hexFileName = ui->fileNameLineEdit->text();
    QFile f2 (hexFileName);	// hexFileName is chosen by the user and is a global variable
    WritePreviousDirectory(returnHexPath()); // Write to the file that keeps track of the previous directory, so we open in the correct dir next time
    f2.open(QIODevice::ReadOnly);	// Open it read only and get the information from the Intel hex file
    QTextStream	OpenStream (&f2);

// First we're filling an array of words with 0xFFFF. These values will be replaced by the appropriate value from the
// Intel hex file if they exist. We will then know what to send.

    Offset = 0;
    lineNumber = 0;
    Address = 0;

    for (j=0; j<MEMORY_ARRAY_SIZE; j++)
    {
        memoryArray[j] = 0xFFFF;
    }

// Now fill the array with relevant data
    while ( !OpenStream.atEnd() )
    {
        s=OpenStream.readLine();		// Read a line as a string and put it in s
        j = s.length();
        QString kStr = s.mid(0,1);		// kStr is a continually recycled temporary string, first get the first character in the line
        for (l=0; l<16; l++)
        {
            LineArray[l] = 0xFFFF;
        }
        if (kStr==":")                              // If it's a colon it's a proper data line
        {
            tempStr = s.mid(1,2);                   // Next is the number of data bytes
            NumberOfBytes = tempStr.toInt(&ok,16);	// Turn the string to an int
            tempStr = s.mid(7,2);                   // Then get the data type
            DataType = tempStr.toInt();             // And turn it into an int
            if (DataType == 0)                      // We are only interested in type 0 data
            {
                tempStr = s.mid(3,4);               // If it's relevant, get the address
                Address = static_cast<quint32>(tempStr.toInt(&ok,16));    // and turn it into an int
                if (Address == 0x80)                // Dummy line to enable use of breakpoints
                {
                    l=0;
                }
                for (l=0; l<NumberOfBytes; l++)     // Then stick the relevant data bytes into the array and replace the 0xFFFF values
                {
                    tempStr = s.mid((9+(l*2)),2);   // Get each byte at a time
                    m = tempStr.toInt(&ok,16);		// Turn into char
                    LineArray[l] = static_cast<quint16>(m);               // Write it into a temporary array of up to sixteen bytes
                }
                tempStr = s.mid((9+(l*2)),2);		// then get a checksum
                for (l=0; l<NumberOfBytes; l++)		// Finally write the temporary array to big array
                {
                    memVal = LineArray[l];
                    if (memVal < 0xFFFF)
                    {
                        addressToProgram = (Offset-0x1000000);
                        addressToProgram += (Address + static_cast<quint32>(l));
                        memoryArray[addressToProgram] = static_cast<quint16>(LineArray[l]);
                    }
                }
            }
            else if (DataType == 4) // This is marking a 32 bit address offset. It will be added to the 65 bit address extracted if the data type is 0
            {
                tempStr = s.mid(9,4);               // Get the offset address
                Offset = static_cast<quint32>(tempStr.toInt(&ok,16));	// and turn it into an int
                Offset <<= 16;
                QString debugString;
                debugString = "Data type " + QString::number(DataType,10) + " Line number " + QString::number(lineNumber,10) + "\n";
                ui->textEdit->insertPlainText(debugString);
            }
            else if (DataType == 01)
            {
                EndAddress = Offset + Address + static_cast<quint32>(l) + 1;
            }
        }
        lineNumber++;
    }
    f2.close();

}




