#ifndef CRC_H
#define CRC_H

#include <QObject>

#include <stdint.h>
#include <QByteArray>
#include <QChar>


union CRCUnion
{

    uint16_t CRCInt;
    uint8_t	CRCChar[2];

};



class CRC
{
public:
    CRC();

public slots:
    void GetCRC(quint16 *Data, quint32 size, union CRCUnion *CRC);
   // uint8_t CheckReceivedFileCRC(uint8_t *Data, union CRCUnion CalculatedFileCRC);
    union CRCUnion getCRCFromString(QString s);

};

#endif // CRC_H
