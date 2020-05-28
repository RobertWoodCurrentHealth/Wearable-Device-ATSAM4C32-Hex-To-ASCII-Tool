#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QFileDialog>
#include <QTextStream>
#include <QByteArray>
#include "CRC.h"


#define MEMORY_ARRAY_SIZE 0x100000    // This is the maximum size of a SAM4C single plane of flash. ie. 1M
#define SAM4C_PAGE_SIZE 512
#define ETX 0x03
#define SPACE 0x20
#define MEMORY_OFFSET 0x1000000

#define UNIX
#define LINUX

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private:
    Ui::MainWindow *ui;
    QString hexFileDirectory;
    QString targetFileName;
    quint16 memoryArray[MEMORY_ARRAY_SIZE];   // Array size of SAM4C
    quint32 startAddress;
    quint32 EndAddress;
    quint32 highestAddress;
    quint32 lowestAddress;
    CRCUnion imageCRC;
    bool firstPage;


private slots:
    void selectHexFile(void);
    QString selectPreviousDirectory(void);
    void fillArray(void);
    QString returnHexPath(void);
    void WritePreviousDirectory(QString prevDir);
    void createTextFile(void);
    QString createPage(uint32_t startAddress);
    bool pageBoundary(uint32_t arrayPosition);
    QString createEraseSection(uint32_t startAddress);
    bool detectDataInPage(quint32 startAddress);

};


#endif // MAINWINDOW_H
