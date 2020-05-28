#include "serial.h"

serial::serial()
{



}


#ifdef UNIX
/* Get ComPorts finds what com ports are available and puts them in a drop down box  */
void serial::GetComPorts(void)
{

// All com ports on Linux are /dev/ttyS* and /dev/ttyUSB* so we will parse the /dev/ directory
    QString Directory = "/dev";
    QDir  d2(Directory);
    QString devTypes;
    d2.setFilter(QDir::System);
    QStringList results;
    QString s;
    QString menuActionName;


    ui->menuSerial_Port->clear();

// Get a QStringList of all the system file items in the /dev directory.
    QStringList devTypesList = d2.entryList();
// then filter out everything except the serial ports
 //   results = devTypesList.filter("ttyS");
  //  results += devTypesList.filter("ttyUS");
#ifdef LINUX
    results += devTypesList.filter("ttyACM");
#elif defined OS_X
    results += devTypesList.filter("tty.usb");
#endif
// Put them in a nice drop down box

    foreach (s,results)
        {
        //ui->debugEdit->setTextColor(Qt::yellow);
       // ui->debugEdit->append(s);
     //   ui->menuSerial_Port->addMenu(s);
        menuActionName = s + "_action";
        QAction *actionPtr = new QAction(s,this);
        actionPtr->setData(s);
        ui->menuSerial_Port->addAction(actionPtr);

        connect(ui->menuSerial_Port,SIGNAL(triggered(QAction *)),this,SLOT(openCrossPlatformSerialPort(QAction *)));
        }

}

#endif
