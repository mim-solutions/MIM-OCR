/*
 * This sample code is a part of the IRIS iDRS library.
 * Copyright (C) 2006-2022 Image Recognition Integrated Systems
 * All rights reserved.
 *
 * This source code is merely intended as a supplement to the iDRS reference and the electronic documentation provided with the library.
 *
 */

#include <idrs.h>
#include <CIDRSLicense.h>

using namespace IDRS;

#define IDRS_SAMPLE_LICENSE_FILE_LOCATION idrs_t("../work/idrs_software_keys_16.inf")

/**
 * Class CSampleSetup provides basic features for IDRS SDK licenses
 */
class CSampleSetup
{
public:
  /**
   * 
   */
  CSampleSetup(IDRS_CTSTR strLicenseFilePath = (IDRS_CTSTR)IDRS_SAMPLE_LICENSE_FILE_LOCATION);

  /**
   * 
   */
  ~CSampleSetup();

  /**
   * Setup the IDRS SDK environment
   */
  IDRS_BOOL SetupIDRS();

  /**
   * Displays the header information for CSampleSetup class
   */
  void DisplayHeaderInformation();

private:
  //! license file path
  IDRS_CHAR m_strLicenseFilePath[IDRS_MAX_PATH];
  //! license type
  IDRS_LICENSE_TYPE m_ltLicenseType;
  //! flag that indicates if OCR module should be loaded
  IDRS_BOOL m_bLoadOcr;
  //! OCR license
  CIDRSLicenseOcr m_objLicenseOcr;
  //! flag that indicates if BARCODE engine module be loaded
  IDRS_BOOL m_bLoadBCode;
  //! Barcode license
  CIDRSLicense m_objLicenseBarcode;
  //! flag that indicates if PREPRO engine module be loaded
  IDRS_BOOL m_bLoadPrepro;
  //! Prepro license
  CIDRSLicense m_objLicensePrepro;
  //! flag that indicates if DOCUMENT OUTPUT engine module be loaded
  IDRS_BOOL m_bLoadDocumentOutput;
  //! DODUMENT OUTPUT license
  CIDRSLicense m_objLicenseDocumentOutput;
  //! flag that indicates if DOCUMENT OUTPUT LITE engine module be loaded
  IDRS_BOOL m_bLoadDocumentOutputLite;
  //! DOCUMENT OUTPUT LITE license
  CIDRSLicense m_objLicenseDocumentOutputLite;
  //! flag that indicates if IMAGE FILE module should be loaded
  IDRS_BOOL m_bLoadImageFile;
  //! Image file license
  CIDRSLicense m_objLicenseImageFile;

  /**
   * Setup the modules for which there's a valid license
   */
  IDRS_BOOL SetupModules ( );

  /**
   * Reads the license information. 
   * See WriteSampleSetupInfo for format specs
   */
  IDRS_BOOL ReadSampleSetupInfo ( );

  /**
   * Writes the licensing information to output file.
   * The format in which the licensing information is written is the following:
   *  - license file
   *  - use barcode engine
   *  - if use barcode engine, license information for barcode module
   *  - use ocr engine
   *  - if use ocr engine, license information for ocr module
   *  - use format module
   *  - if use format module, license information for format module
   *  - use image file
   *  - if use image file, license information for image file module
   *  - use prepro
   *  - if use prepro, license information for prepro module
   */
  IDRS_INT WriteSampleSetupInfo ( );

  /**
   * Reads CIDRSLicense object from supplied file.
   * 
   * \param pFile - file handle containing the data to read
   * \param argLicense - reference to the license object to be updated
   * \param rbLoadModule - reference to a boolean flag indicating if the license needs to be loaded or not.
   *
   * If rbLoadModule is IDRS_FALSE then the license information is not present in the file and the argLicense object is not updated
   *
   * \retval IDRS_TRUE if the license can be read successfully or rbLoadModule is IDRS_FALSE
   * \retval IDRS_FALSE if the license cannot be read successfully
   */
  IDRS_BOOL ReadLicenseInfo(FILE *pFile, CIDRSLicense & argLicense, IDRS_BOOL & rbLoadModule);

  /**
   * Reads CIDRSLicenseOcr object from the supplied file.
   * 
   * \param pFile - file handle containing the data to read
   * \param argLicense - reference to the license object to be updated
   * \param rbLoadModule - reference to a boolean flag indicating if the license needs to be loaded or not.
   *
   * If rbLoadModule is IDRS_FALSE then the license information is not present in the file and the argLicense object is not updated
   *
   * \retval IDRS_TRUE if the license can be read successfully or rbLoadModule is IDRS_FALSE
   * \retval IDRS_FALSE if the license cannot be read successfully
   */
  IDRS_BOOL ReadLicenseInfo(FILE *pFile, CIDRSLicenseOcr & argLicense, IDRS_BOOL & rbLoadModule);

  /**
   * Writes an string with a fixed length
   */
  /**
   * \brief Write a string with a fixed length to a FILE
   *
   * \param fp File pointer, opened using fopen
   * \param str Text to be written to file
   * \param uiSize Size of the buffer to be written to the file.
   * If the size of the buffer is larger than the text, NULL characters will be appended.
   * If the size of the text is greater than the uiSize, the function will copy only uiSize characters, without including the null-terminating character
   *
   * \return IDRS_TRUE if the text has been successfully written to the output file, IDRS_FALSE otherwise
   */
  IDRS_BOOL Write(FILE * fp, IDRS_CSTR str, IDRS_UINT32 uiSize);

  /**
   * Writes a CIDRSLicense license to file
   */
  IDRS_BOOL WriteLicenseInfo(FILE* fp, const CIDRSLicense& argLicense, const IDRS_BOOL bLoadLicense);

  /**
   * Writes a CIDRSLicenseOcr license to file
   */
  IDRS_BOOL WriteLicenseInfo(FILE * fp, const CIDRSLicenseOcr& argLicense, const IDRS_BOOL bLoadLicense);

  /**
   * Displays the setup information when loading licenses from a file or reading licenses from console.
   */
  void DisplaySetupInformation();
  /**
   * Reads a boolean answer from the console.
   */
  IDRS_BOOL GetAnswerFromConsole(IDRS_CHAR chTrue = 'y', IDRS_CHAR chFalse = 'n');
  /**
   * Reads the software key for an extension
   *
   * \param strExtensionName - the name of the extension. Eg. IDRS_OCR_EXTENSION_ASIAN
   * \param uiExtensionIndex - index of the extension
   * \param argLicense - the license to be updated with extension license information
   */
  void GetLicenseForExtension(IDRS_CSTR strExtensionName, IDRS_UINT32 uiExtensionIndex, CIDRSLicense& argLicense);

  /**
   * Displays an interactive menu for obtaining the license information from the console
   */
  void ReadLicenseInfoFromConsole();

  /**
   * Read a character from the stdin.
   *
   * \return the character read
   */
  IDRS_CHAR ReadCharacterFromConsole ();

  /**
   * Read a string from the stdin and store it in the given buffer.
   *
   * \param strBuffer the buffer to store to
   * \param uiBufferSize the size of the buffer
   * \return IDRS_TRUE if the string is entirely contained in the provided buffer, IDRS_FALSE if the string was too long or if an error occured while reading it
   * \note even if the string was longer than the buffer, it will still be consumed so that next calls are not affected.
   */
  IDRS_BOOL ReadStringFromConsole ( IDRS_CHAR* strBuffer, IDRS_UINT uiBufferSize );

  /**
   * \brief Template function that writes an element to a file. The function has a template parameters specifying the date type to be written
   *
   * \param fp File pointer obtained after a successful call to fopen
   * \param value Value to be written to the file
   *
   * \return IDRS_TRUE if the data has been written successfully to the file, IDRS_FALSE otherwise
   */
  template<typename T>
  IDRS_BOOL Write(FILE * fp, T value)
  {
    if (fp == NULL)
    {
      return IDRS_FALSE;
    }

    return fwrite(&value, sizeof(T), 1, fp) == 1 ? IDRS_TRUE : IDRS_FALSE;
  }
};
