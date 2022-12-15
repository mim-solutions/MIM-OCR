/*
 * This sample code is a part of the IRIS iDRS library.
 * Copyright (C) 2006-2022 Image Recognition Integrated Systems
 * All rights reserved.
 *
 * This source code is merely intended as a supplement to the iDRS reference and the electronic documentation provided with the library.
 *
 */

#include "CSampleSetup.h"
#include <ctype.h>

#ifdef IDRS_OS_WIN
#include "CRegistryLicense.h"
#endif

/*
 *  
 */
CSampleSetup::CSampleSetup(IDRS_CTSTR strLicenseFilePath)
{
  m_bLoadOcr = IDRS_FALSE;
  m_bLoadBCode = IDRS_FALSE;
  m_bLoadPrepro = IDRS_FALSE;
  m_bLoadDocumentOutput = IDRS_FALSE;
  m_bLoadDocumentOutputLite = IDRS_FALSE;
  m_bLoadImageFile = IDRS_FALSE;

  idrs_tchar2char (m_strLicenseFilePath, strLicenseFilePath);
}

/*
 *  
 */
CSampleSetup::~CSampleSetup()
{
}

/*
 *
 */
IDRS_CHAR CSampleSetup::ReadCharacterFromConsole ()
{
  IDRS_CHAR strInput [ 2 ];
  IDRS_BOOL bIsOneCharAnswer;
  do
  {
    bIsOneCharAnswer = ReadStringFromConsole ( strInput, 2 );
  } while ( ! bIsOneCharAnswer );
  return strInput [ 0 ];
}

/*
 *
 */
IDRS_BOOL CSampleSetup::ReadStringFromConsole ( IDRS_CHAR* strBuffer, IDRS_UINT uiBufferSize )
{
  // read the string - return IDRS_FALSE if an error occurs there
  if ( fgets ( strBuffer, uiBufferSize, stdin ) == NULL )
  {
    printf ( "\n" );
    return IDRS_FALSE;
  }
  // if the string was too long for the buffer, check if there were some real extra characters (other than newline or end of stream)
  // and consumes them, before returning status
  if ( strBuffer [ strlen ( strBuffer ) - 1 ] != '\n' )
  {
    IDRS_BOOL bExtraCharacters = IDRS_FALSE;
    IDRS_INT iChar;
    while (( iChar = getchar ()) != '\n' && iChar != EOF )
    {
      bExtraCharacters = IDRS_TRUE;
    }
    printf ( "\n" );
    return ! bExtraCharacters;
  }
  // remove the newline then return success
  strBuffer [ strlen ( strBuffer ) - 1 ] = 0;
  printf ( "\n" );
  return IDRS_TRUE;
}

/*
 *  
 */
IDRS_BOOL CSampleSetup::GetAnswerFromConsole(IDRS_CHAR chTrue, IDRS_CHAR chFalse)
{
  IDRS_CHAR chInput;
  do
  {
    chInput = ReadCharacterFromConsole ();
  } while (( toupper ( chTrue ) != toupper ( chInput )) && ( toupper ( chFalse ) != toupper ( chInput )));
  
  return ( toupper ( chTrue ) == toupper ( chInput )) ? IDRS_TRUE : IDRS_FALSE;
}

/*
 *  
 */
IDRS_BOOL CSampleSetup::SetupIDRS()
{
  DisplayHeaderInformation();

  IDRS_BOOL bLicenseLoadedFromFileOrRegistry = IDRS_FALSE;

#ifdef IDRS_OS_WIN
  bLicenseLoadedFromFileOrRegistry = CRegistryLicense::AreSoftwareKeysInRegistry();
  if (bLicenseLoadedFromFileOrRegistry)
  {
//    printf ( "Do you want to setup iDRS with the information contained in registry (y/n)?\n" );

//    if (GetAnswerFromConsole('y', 'n') == IDRS_TRUE)
    if(1)
    {
      bLicenseLoadedFromFileOrRegistry = IDRS_TRUE;

      CRegistryLicense::ReadLicenseKeysFromRegistry(m_objLicenseBarcode, m_objLicensePrepro, m_objLicenseDocumentOutput, m_objLicenseImageFile, m_objLicenseOcr,
        m_bLoadBCode, m_bLoadPrepro, m_bLoadDocumentOutput, m_bLoadImageFile, m_bLoadOcr);
    }
    else
    {
      bLicenseLoadedFromFileOrRegistry = IDRS_FALSE;
    }
  }

  if (bLicenseLoadedFromFileOrRegistry == IDRS_FALSE)
  {
#endif

  bLicenseLoadedFromFileOrRegistry = ReadSampleSetupInfo();
  if (bLicenseLoadedFromFileOrRegistry)
  {
    // the license information has been found. ask the user if this information should be used to setup IDRS SDK
    printf ( "SetupIDRS has detected an existing %s file.\n", m_strLicenseFilePath );
//    printf ( "Do you want to setup iDRS with the information contained in this file (y/n)?\n" );
//
//    if (GetAnswerFromConsole('y', 'n') == IDRS_FALSE)
    if (0)
    {
      bLicenseLoadedFromFileOrRegistry = IDRS_FALSE;
    }
  }

#ifdef IDRS_OS_WIN
  }
#endif

  if ( bLicenseLoadedFromFileOrRegistry == IDRS_FALSE )
  {
    DisplaySetupInformation();
    // could not load the license information from the file. ask the user for licenses
    ReadLicenseInfoFromConsole();
  }

  IDRS_BOOL bSetupResult = SetupModules();

  if ( bSetupResult == IDRS_FALSE )
  {
    return IDRS_FALSE;
  }
  else if ( bLicenseLoadedFromFileOrRegistry == IDRS_FALSE )
  {
    // if the licenses were introduced by the user, ask whether to save them to a file
    printf ( "The setup was successful.\n" );
    printf ( "This sample can save the information you enter to the %s file,", m_strLicenseFilePath );
    printf ( " so you won't have to re-enter the information next time you'll run this application.\n" );
    printf ( "Do you want to save the information you entered to the %s file (y/n)?\n", m_strLicenseFilePath );

    if (GetAnswerFromConsole() == IDRS_TRUE)
    {
      if (WriteSampleSetupInfo() != 0)
      {
        printf ( "There was an error while writing the setup information!\n" );
      }
    }
  }
  return IDRS_TRUE;
}

/*
 *
 */
void CSampleSetup::DisplayHeaderInformation()
{
  printf ( "\nSetup iDRS16 SDK environment.\n\n" );
  printf ( "The CSampleSetup class is an example how to setup the iDRS16 SDK.\n" );
  printf ( "Its full source code is available in the CSampleSetup.cpp and CSampleSetup.h files located in samples%ccpp%cCommon.\n\n",
    IDRS_OS_DIR_SEP_CHAR, IDRS_OS_DIR_SEP_CHAR );
}

/*
 *
 */
void CSampleSetup::DisplaySetupInformation()
{
  printf ( "iDRS is composed of many different modules, modular to your project requirements.\n" );
  printf ( "During this step of the sample application, you will be asked all the information needed to setup the iDRS:\n" );
  printf ( "- your license type\n" );
  printf ( "- the modules and the extensions you want to load\n" );
  printf ( "- the corresponding software keys\n\n" );
  printf ( "At the end of the application, if SetupIDRS succeeds, the application will propose you to save the settings to the %s file.",
   m_strLicenseFilePath );
  printf ( " So the next time you run a sample you won't have to re-enter these information.\n\n" );
}

/*
 *  
 */
void CSampleSetup::ReadLicenseInfoFromConsole()
{
  IDRS_CHAR chInput;
  IDRS_CHAR strSoftwareKey[IDRS_LICENSE_MAX_SIZE] = {0};
  IDRS_CHAR strExtensionName[IDRS_MAX_PATH] = {0};

  m_bLoadOcr = IDRS_FALSE;
  m_bLoadBCode = IDRS_FALSE;
  m_bLoadPrepro = IDRS_FALSE;
  m_bLoadDocumentOutput = IDRS_FALSE;
  m_bLoadImageFile = IDRS_FALSE;
  m_objLicenseOcr = NULL;
  m_objLicenseBarcode = NULL;
  m_objLicensePrepro = NULL;
  m_objLicenseDocumentOutput = NULL;
  m_objLicenseImageFile = NULL;

  // Getting the information from the user
  printf ( "License type selection\n" );
  printf ( "2 - IDRS_LICENSE_CUSTOM_SOFTWARE - Custom software\n" );
  printf ( "Please enter your iDRS license type:\n" );
  do
  {
    chInput = ReadCharacterFromConsole ();
  } while ( chInput != '2' );
  m_ltLicenseType =  IDRS_LICENSE_CUSTOM_SOFTWARE;

  printf ( "SetupIDRS will ask you for your software keys.\n" );

  // IDRS_MODULE_OCR

  printf ( "IDRS_MODULE_OCR\n" );
  printf ( "IDRS_MODULE_OCR is the ocr engine.\n" );
  printf ( "Do you have a license for the IDRS_MODULE_OCR module (y/n)?\n" );

  m_bLoadOcr = GetAnswerFromConsole();
  if ( m_bLoadOcr )
  {
    printf ( "Getting information for the IDRS_MODULE_OCR module.\n" );
    printf ( "Please enter IDRS_MODULE_OCR software key:\n" );

    ReadStringFromConsole ( strSoftwareKey, IDRS_LICENSE_MAX_SIZE );

    m_objLicenseOcr = CIDRSLicenseOcr(m_ltLicenseType, strSoftwareKey);
      
    for ( IDRS_UINT32 uiExtensionId = 0; uiExtensionId < IDRS_OCR_EXTENSION_COUNT; uiExtensionId ++ )
    {
      switch ( m_objLicenseOcr.GetExtensionAt(uiExtensionId))
      {
        case IDRS_OCR_EXTENSION_HEBREW:
          printf ( "IDRS_OCR_EXTENSION_HEBREW extends the OCR languages with the Hebrew language.\n" );
          sprintf ( strExtensionName, "IDRS_OCR_EXTENSION_HEBREW" );
          break;

        case IDRS_OCR_EXTENSION_BANKING_FONTS:
          printf ( "IDRS_OCR_EXTENSION_BANKING_FONTS allows to recognize the following banking fonts:\n" );
          printf ( "- OCR-A\n" );
          printf ( "- OCR-B\n" );
          printf ( "- E13B\n" );
          printf ( "- CMC-7\n" );
          sprintf ( strExtensionName, "IDRS_OCR_EXTENSION_BANKING_FONTS" );
          break;
            
        case IDRS_OCR_EXTENSION_HAND_WRITE:
          printf ( "IDRS_OCR_EXTENSION_HAND_WRITE is the standard HAND_WRITE extension.\n" );
          printf ( "The IRIS Intelligent Character Recognition (HAND_WRITE) engine allows you to recognize all handwritten characters based on the Latin" );
          printf ( " alphabet.\n" );
          sprintf ( strExtensionName, "IDRS_OCR_EXTENSION_HAND_WRITE" );
          break;

        case IDRS_OCR_EXTENSION_ARABIC:
          printf ( "IDRS_OCR_EXTENSION_ARABIC extends the OCR languages with the Arabic and Farsi languages.\n" );
          sprintf ( strExtensionName, "IDRS_OCR_EXTENSION_ARABIC" );
          break;

        case IDRS_OCR_EXTENSION_ASIAN2:
          printf ( "IDRS_OCR_EXTENSION_ASIAN2 extends the OCR languages with for 4 additional languages:\n" );
          printf("- Traditional Chinese\n");
          printf("- Simplified Chinese\n");
          printf("- Japanese\n");
          printf("- Korean\n");
          printf ( "Please note that IDRS_OCR_EXTENSION_ASIAN3, IDRS_OCR_EXTENSION_ASIAN2 cannot be enabled at the same time\n" );
          sprintf ( strExtensionName, "IDRS_OCR_EXTENSION_ASIAN2" );
          break;

#if defined(IDRS_OS_WIN) || defined(IDRS_OS_LINUX)
        case IDRS_OCR_EXTENSION_ASIAN3:
          printf ( "IDRS_OCR_EXTENSION_ASIAN3 represents a combination of IRIS Asian engine (Asian2) with a 3rd party OCR Engine,\n" );
          printf ( "which allows to improve speed performance without compromising accuracy.\n" );
          printf ( "Please note that IDRS_OCR_EXTENSION_ASIAN3, IDRS_OCR_EXTENSION_ASIAN2 cannot be enabled at the same time\n" );
          sprintf ( strExtensionName, "IDRS_OCR_EXTENSION_ASIAN3" );
          break;
#endif
        default:
          strExtensionName [ 0 ] = 0;
          break;
      }

      GetLicenseForExtension(strExtensionName, uiExtensionId, m_objLicenseOcr);
    }

#ifdef IDRS_OS_WIN
    // get the ocr resources
    while ( IDRS_TRUE )
    {
      IDRS_CHAR strResourcesPath[IDRS_MAX_PATH ] = {0};
      IDRS_TCHAR tstrResourcesPath[IDRS_MAX_PATH] = {0};
      
      const IDRS_CSTR strResourceToCheck = "eng.ilex";
      IDRS_CHAR strTempPath[IDRS_MAX_PATH] = {0};

      printf ( "Please enter the path to the OCR resource directory (the directory containing the .ilex files)\n" );
      printf ( "(Just enter '#' for C:\\Program Files\\I.R.I.S. SA\\iDRS\\resources)\n" );
      fflush ( stdin );
      memset(strResourcesPath, 0, IDRS_MAX_PATH*sizeof(IDRS_CHAR));
      memset(tstrResourcesPath, 0, IDRS_MAX_PATH*sizeof(IDRS_TCHAR));
      ReadStringFromConsole(strResourcesPath, IDRS_MAX_PATH);

      if ( strcmp ( strResourcesPath, "#" ) == 0 )
      {
        sprintf ( strResourcesPath, "C:\\Program Files\\I.R.I.S. SA\\iDRS\\resources" );
      }

      if ( strlen ( strResourcesPath ))
      {
        sprintf ( strTempPath, "%s\\%s", strResourcesPath, strResourceToCheck );
      }
      else
      {
        sprintf ( strTempPath, strResourceToCheck );
      }

      idrs_char2tchar(tstrResourcesPath, strResourcesPath);
      m_objLicenseOcr.SetResourcesPath(tstrResourcesPath);

      if ( _access ( strTempPath, 0 ) != 0 )
      {
        printf ( "\tWARNING - The english lexicon file %s cannot be found.\n", strTempPath );
        printf ( "Maybe you made a mistake when typing the path to the OCR resource directory.\n" );
        printf ( "Double check the path to the OCR resource directory.\n" );
        printf ( "Do you want to continue anyway or do you want to re-enter the path to the OCR resource directory (c/r)?\n" );

        if (GetAnswerFromConsole('c', 'r') == IDRS_TRUE)
        {
          break;
        }
      }
      else
      {
        break;
      }
    }
#else
    m_objLicenseOcr.SetResourcesPath(idrs_t(""));
#endif
  }


  // IDRS_MODULE_BARCODE
  printf ( "IDRS_MODULE_BARCODE\n" );
  printf ( "IDRS_MODULE_BARCODE is the barcode recognition engine.\n" );
  printf ( "The barcode module will identify barcodes located anywhere on the page.\n" );
  printf ( "The barcodes can be used as separators and their content can be used for renaming files for example.\n" );
  printf ( "Do you have a license for the IDRS_MODULE_BARCODE module (y/n)?\n" );

  m_bLoadBCode = GetAnswerFromConsole();

  if ( m_bLoadBCode )
  {
    memset ( strSoftwareKey, 0, IDRS_LICENSE_MAX_SIZE * sizeof(IDRS_CHAR));

    printf ( "Getting information for the IDRS_MODULE_BARCODE module.\n" );
    printf ( "Please enter IDRS_MODULE_BARCODE software key:\n" );
    ReadStringFromConsole ( strSoftwareKey, IDRS_LICENSE_MAX_SIZE );

    m_objLicenseBarcode = CIDRSLicense(IDRS_MODULE_BARCODE, m_ltLicenseType, strSoftwareKey);

    for ( IDRS_UINT32 uiExtensionId = 0; uiExtensionId < IDRS_BARCODE_EXTENSION_COUNT; uiExtensionId ++ )
    {
      switch ( m_objLicenseBarcode.GetExtensionAt(uiExtensionId) )
      {
        case IDRS_BARCODE_EXTENSION_PDF417:
          printf ( "The IDRS_BARCODE_EXTENSION_PDF417 extension offers the recognition of the PDF 417 barcodes.\n" );
          sprintf ( strExtensionName, "IDRS_BARCODE_EXTENSION_PDF417" );
          break;

        case IDRS_BARCODE_EXTENSION_QRCODE:
          printf ( "The IDRS_BARCODE_EXTENSION_QRCODE extension offers the recognition of the QR barcodes.\n" );
          sprintf ( strExtensionName, "IDRS_BARCODE_EXTENSION_QRCODE" );
          break;

        case IDRS_BARCODE_EXTENSION_ENGINE_EVO_I:
          printf ( "The IDRS_BARCODE_EXTENSION_ENGINE_EVO_I extension offers the possibility of using an additional barcode\n" );
          printf ( "engine, for better performances.\n" );
          sprintf ( strExtensionName, "IDRS_BARCODE_EXTENSION_ENGINE_EVO_I" );
          break;

        case IDRS_BARCODE_EXTENSION_DATAMATRIX:
          printf ( "The IDRS_BARCODE_EXTENSION_DATAMATRIX extension offers the recognition of the DataMatrix barcodes.\n" );
          sprintf ( strExtensionName, "IDRS_BARCODE_EXTENSION_DATAMATRIX" );
          break;

        default:
          strExtensionName [ 0 ] = 0;
          break;
      }

      GetLicenseForExtension(strExtensionName, uiExtensionId, m_objLicenseBarcode);
    }
  }

  // IDRS_MODULE_PREPRO
  printf ( "IDRS_MODULE_PREPRO\n" );
  printf ( "IDRS_MODULE_PREPRO is the standard image pre-processing module.\n" );
  printf ( "Before doing the OCR, the images may need to be optimized for the OCR process. This is done by different pre-processing functions.\n" );
  printf ( "The IDRS_MODULE_PREPRO module allows you to clean-up the images for optimized OCR such as deskew, despeckle, binarize, etc.\n" );
  printf ( "Do you have a license for the IDRS_MODULE_PREPRO module (y/n)?\n" );
  
  m_bLoadPrepro = GetAnswerFromConsole();

  if ( m_bLoadPrepro )
  {
    memset ( strSoftwareKey, 0, IDRS_LICENSE_MAX_SIZE * sizeof(IDRS_CHAR));

    printf ( "Getting information for the IDRS_MODULE_PREPRO module.\n" );
    printf ( "Please enter IDRS_MODULE_PREPRO software key:\n" );
    ReadStringFromConsole ( strSoftwareKey, IDRS_LICENSE_MAX_SIZE );

    m_objLicensePrepro = CIDRSLicense(IDRS_MODULE_PREPRO, m_ltLicenseType, strSoftwareKey);

    for ( IDRS_UINT32 uiExtensionId = 0; uiExtensionId < IDRS_PREPRO_EXTENSION_COUNT; uiExtensionId ++ )
    {
      switch ( m_objLicensePrepro.GetExtensionAt(uiExtensionId) )
      {
        case IDRS_PREPRO_EXTENSION_ADVANCED_PREPRO:
          printf ( "IDRS_PREPRO_EXTENSION_ADVANCED_PREPRO is the advanced pre-processing extension.\n" );
          printf ( "This extension allows to do black border removal, line removal, advanced despeckle, color conversion, etc.\n" );
          sprintf ( strExtensionName, "IDRS_PREPRO_EXTENSION_ADVANCED_PREPRO" );
          break;
        case IDRS_PREPRO_EXTENSION_MOBILE_CAPTURE:
          printf ( "IDRS_PREPRO_EXTENSION_MOBILE_CAPTURE offers perspective image correction for pictures taken with camera.\n" );
          sprintf ( strExtensionName, "IDRS_PREPRO_EXTENSION_MOBILE_CAPTURE" );
          break;
        default:
          strExtensionName [ 0 ] = 0;
          break;
      }

      GetLicenseForExtension(strExtensionName, uiExtensionId, m_objLicensePrepro);
    }
  }

  // IDRS_MODULE_DOCUMENT_OUTPUT

    printf ( "IDRS_MODULE_DOCUMENT_OUTPUT\n" );
    printf ( "IDRS_MODULE_DOCUMENT_OUTPUT is the formatting module.\n" );
    printf ( "Once the recognition of the document has been done, you might still need to generate an output file.\n" );
    printf ( "This is done by the document output module.\n" );
    printf ( "Do you have a license for the IDRS_MODULE_DOCUMENT_OUTPUT module (y/n)?\n" );
    
    m_bLoadDocumentOutput = GetAnswerFromConsole();

    if ( m_bLoadDocumentOutput )
    {
      printf ( "Getting information for the IDRS_MODULE_DOCUMENT_OUTPUT module.\n" );

      memset ( strSoftwareKey, 0, IDRS_LICENSE_MAX_SIZE * sizeof(IDRS_CHAR));

      printf ( "Please enter IDRS_MODULE_DOCUMENT_OUTPUT software key:\n" );
      ReadStringFromConsole ( strSoftwareKey, IDRS_LICENSE_MAX_SIZE );

      m_objLicenseDocumentOutput = CIDRSLicense(IDRS_MODULE_DOCUMENT_OUTPUT, m_ltLicenseType, strSoftwareKey);

      for ( IDRS_UINT32 uiExtensionId = 0; uiExtensionId < IDRS_DOCUMENT_OUTPUT_EXTENSION_COUNT; uiExtensionId ++ )
      {
        switch ( m_objLicenseDocumentOutput.GetExtensionAt(uiExtensionId) )
        {
          case IDRS_DOCUMENT_OUTPUT_IHQC_EXTENSION:
            printf ( "IDRS_DOCUMENT_OUTPUT_IHQC_EXTENSION is the intelligent High Quality compression extension.\n" );
            sprintf ( strExtensionName, "IDRS_DOCUMENT_OUTPUT_IHQC_EXTENSION" );
            break;

          case IDRS_DOCUMENT_OUTPUT_JPEG2000_EXTENSION:
            printf ( "IDRS_DOCUMENT_OUTPUT_JPEG2000_EXTENSION enables JPEG2000 compression to DOCUMENT OUTPUT module.\n" );
            sprintf ( strExtensionName, "IDRS_DOCUMENT_OUTPUT_JPEG2000_EXTENSION" );
            break;

          default:
            strExtensionName [ 0 ] = 0;
            break;
        }

        GetLicenseForExtension(strExtensionName, uiExtensionId, m_objLicenseDocumentOutput);
      }
    }

  // IDRS_MODULE_IMAGE_FILE

  printf ( "IDRS_MODULE_IMAGE_FILE\n" );
  printf ( "IDRS_MODULE_IMAGE_FILE is the iDRS imaging module.\n" );
  printf ( "This module allows you to open the most known input formats including TIFF G4 and BMP.\n" );
  printf ( "Do you have a license for the IDRS_MODULE_IMAGE_FILE module (y/n)?\n" );
  m_bLoadImageFile = GetAnswerFromConsole();

  if ( m_bLoadImageFile )
  {
    memset ( strSoftwareKey, 0, IDRS_LICENSE_MAX_SIZE * sizeof(IDRS_CHAR));

    printf ( "Getting information for the IDRS_MODULE_IMAGE_FILE module.\n" );
    printf ( "Please enter IDRS_MODULE_IMAGE_FILE software key:\n" );
    ReadStringFromConsole ( strSoftwareKey, IDRS_LICENSE_MAX_SIZE );

    m_objLicenseImageFile = CIDRSLicense(IDRS_MODULE_IMAGE_FILE, m_ltLicenseType, strSoftwareKey);

    for ( IDRS_UINT32 uiExtensionId = 0; uiExtensionId < IDRS_IMAGE_FILE_EXTENSION_COUNT; uiExtensionId ++ )
    {
      switch ( m_objLicenseImageFile.GetExtensionAt(uiExtensionId) )
      {
        case IDRS_FILE_EXTENSION_JPEG2000:
          printf ( "IDRS_FILE_EXTENSION_JPEG2000 is the JPEG2000 extension.\n" );
          sprintf ( strExtensionName, "IDRS_FILE_EXTENSION_JPEG2000" );
          break;

        case IDRS_FILE_EXTENSION_JBIG2:
          printf ( "IDRS_FILE_EXTENSION_JBIG2 is the JBIG2 extension.\n" );
          sprintf ( strExtensionName, "IDRS_FILE_EXTENSION_JBIG2" );
          break;
// ask for pdf as input license on windows and linux plaforms only
#if defined(IDRS_OS_WIN) || defined(IDRS_OS_LINUX)
        case IDRS_FILE_EXTENSION_PDF:
          printf ( "IDRS_FILE_EXTENSION_PDF enables pdf as input.\n" );
          sprintf ( strExtensionName, "IDRS_FILE_EXTENSION_PDF" );
          break;
#endif
        default:
          strExtensionName [ 0 ] = 0;
          break;
      }

      GetLicenseForExtension(strExtensionName, uiExtensionId, m_objLicenseImageFile);
    }
  }
}

/*
 *  
 */
void CSampleSetup::GetLicenseForExtension(IDRS_CSTR strExtensionName, IDRS_UINT32 uiExtensionIndex, CIDRSLicense& argLicense)
{
  IDRS_CHAR strSoftwareKey[IDRS_LICENSE_MAX_SIZE] = {0};
  if ( strExtensionName [ 0 ] == 0 )
  {
  }
  else
  {
    printf ( "Do you have a license for the %s extension (y/n)?\n", strExtensionName );

    if (GetAnswerFromConsole() == IDRS_TRUE)
    {
      printf ( "Please enter %s software key:\n", strExtensionName );
      ReadStringFromConsole ( strSoftwareKey, IDRS_LICENSE_MAX_SIZE );

      argLicense.EnableExtension(argLicense.GetExtensionAt(uiExtensionIndex), strSoftwareKey);
    }
  }

  printf ( "\n" );
}

/*
 *
 */
IDRS_BOOL CSampleSetup::SetupModules ( )
{
  // setup the licenses for the modules
  
  try
  {
    if ( m_bLoadOcr )
    {
      printf ( "Loading IDRS_MODULE_OCR\n" );
      CIDRSSetup::SetupModule ( m_objLicenseOcr );
    }

    if ( m_bLoadBCode )
    {
      printf ( "Loading IDRS_MODULE_BARCODE\n" );
      CIDRSSetup::SetupModule ( m_objLicenseBarcode );
    }

    if ( m_bLoadPrepro )
    {
      printf ( "Loading IDRS_MODULE_PREPRO\n" );
      CIDRSSetup::SetupModule ( m_objLicensePrepro );
    }

    if ( m_bLoadDocumentOutput )
    {
      printf ( "Loading IDRS_MODULE_DOCUMENT_OUTPUT\n" );
      CIDRSSetup::SetupModule ( m_objLicenseDocumentOutput );
    }
    
    if ( m_bLoadImageFile )
    {
      printf ( "Loading IDRS_MODULE_IMAGE_FILE\n" );
      CIDRSSetup::SetupModule ( m_objLicenseImageFile );
    }

    printf ( "%s setup complete!\n", CIDRSSetup::GetIdrsDescription ());
  }
  catch ( const CIDRSException & objIDRSException )
  {
    printf ( "\tAn error occurred in the iDRS.\n" );
    printf ( "\tCode %lu\n", objIDRSException.m_code );
    printf ( "\tFile %s\n", objIDRSException.m_strSrcFile );
    printf ( "\tLine %u\n", objIDRSException.m_uiSrcLine );

    switch ( objIDRSException.m_code )
    {
      case IDRS_ERROR_TEMPORARY_LICENSE_EXPIRED:
        printf ( "\tPossible reason: Your software license expired.\n" );
        break;
      case IDRS_ERROR_CHARACTER_RECOGNITION_ENGINE_INVALID_KEY:
        printf ( "\tPossible reason: Please check your software keys for IDRS_MODULE_OCR.\n" );
        break;
      case IDRS_ERROR_BARCODE_INVALID_KEY:
        printf ( "\tPossible reason: Please check your software keys for IDRS_MODULE_BARCODE.\n" );
        break;
      case IDRS_ERROR_PREPRO_INVALID_KEY:
        printf ( "\tPossible reason: Please check your software keys for IDRS_MODULE_PREPRO.\n" );
        break;
      case IDRS_ERROR_DOCUMENT_OUTPUT_INVALID_KEY:
        printf ( "\tPossible reason: Please check your software keys for IDRS_MODULE_DOCUMENT_OUTPUT.\n" );
        break;
      case IDRS_ERROR_IMAGE_FILE_INVALID_KEY:
        printf ( "\tPossible reason: Please check your software keys for IDRS_MODULE_IMAGE_FILE.\n" );
        break;
      default:
        printf ( "Please check your settings and the license type.\n" );
        break;
    }
    CIDRSSetup::Unload ();
    return IDRS_FALSE;
  }

  return IDRS_TRUE;
}

/*
 *  
 */
IDRS_BOOL CSampleSetup::ReadLicenseInfo(FILE *pFile, CIDRSLicense & argLicense, IDRS_BOOL & rbLoadModule)
{
  IDRS_BOOL bRetValue = IDRS_FALSE;

  // read flag that indicates if the extension is enabled or not
  if (fread(&rbLoadModule, sizeof(IDRS_BOOL), 1, pFile) == 1)
  {
    if (rbLoadModule)
    {
      IDRS_MODULE mModule;
      IDRS_LICENSE_TYPE ltLicenseType;
      IDRS_CHAR strLicenseKey[IDRS_LICENSE_MAX_SIZE] = {0};
      IDRS_UINT32 uiExtensionCount = 0;
      // read extension information
      if ((fread(&mModule, sizeof(IDRS_MODULE), 1, pFile) == 1) && 
        (fread(&ltLicenseType, sizeof(IDRS_LICENSE_TYPE), 1, pFile) == 1) && 
        (fread(strLicenseKey, sizeof(IDRS_CHAR), IDRS_LICENSE_MAX_SIZE, pFile) == IDRS_LICENSE_MAX_SIZE))
      {
        argLicense = CIDRSLicense(mModule, ltLicenseType, strLicenseKey);

        // read the number of extensions
        if (fread(&uiExtensionCount, sizeof(IDRS_UINT), 1, pFile) == 1)
        {
          bRetValue = IDRS_TRUE;

          // read each extension
          for (IDRS_UINT32 uiIndex = 0; uiIndex < uiExtensionCount; uiIndex++)
          {
            IDRS_CHAR strExtensionLicenseKey[IDRS_LICENSE_MAX_SIZE] = {0};
            IDRS_UINT bExtensionEnabled;

            // read flag indicating wheter the extension is enabled or not
            if (fread(&bExtensionEnabled, sizeof(IDRS_UINT), 1, pFile) == 1)
            {
              if (bExtensionEnabled == 1)
              {
                // if the extension is enabled, read the extension's license key
                if (fread(strExtensionLicenseKey, sizeof(IDRS_CHAR), IDRS_LICENSE_MAX_SIZE, pFile) == IDRS_LICENSE_MAX_SIZE)
                {
                  argLicense.EnableExtension(argLicense.GetExtensionAt(uiIndex), strExtensionLicenseKey);
                }
                else
                {
                  bRetValue = IDRS_FALSE;
                  break;
                }
              }
            }
            else
            {
              bRetValue = IDRS_FALSE;
              break;
            }
          }
        }
      }
    }
    else
    {
      bRetValue = IDRS_TRUE;
    }
  }

  return bRetValue;
}

/*
 *
 */
IDRS_BOOL CSampleSetup::ReadLicenseInfo(FILE *pFile, CIDRSLicenseOcr & argLicense, IDRS_BOOL & rbLoadModule)
{
  IDRS_BOOL bRetValue = IDRS_FALSE;

  CIDRSLicense objTempLicense;
  // read the standard license information in a temporary CIDRSLicense object
  if (ReadLicenseInfo(pFile, objTempLicense, rbLoadModule) == IDRS_TRUE)
  {
    bRetValue = IDRS_TRUE;
    if (rbLoadModule)
    {
      IDRS_CHAR strOcrPath[IDRS_MAX_PATH] = {0};
      IDRS_TCHAR tstrOcrPath[IDRS_MAX_PATH] = {0};
      // read the path to resources
      if (fread(strOcrPath, sizeof(IDRS_CHAR), IDRS_MAX_PATH, pFile) == IDRS_MAX_PATH)
      {
        // convert the path to unicode
        idrs_char2tchar(tstrOcrPath, strOcrPath);

        // create the ocr license
        argLicense = CIDRSLicenseOcr(objTempLicense.GetLicenseType(), objTempLicense.GetSoftwareKey(), tstrOcrPath);

        // enable the extension
        for (IDRS_UINT uiIndex = 0; uiIndex < argLicense.GetExtensionCount(); uiIndex++)
        {
          IDRS_EXTENSION eExtension = argLicense.GetExtensionAt ( uiIndex );
          if ( objTempLicense.IsExtensionEnabled ( eExtension ))
          {
            argLicense.EnableExtension ( eExtension, 
              objTempLicense.GetExtensionSoftwareKey ( eExtension ));
          }
        }
      }
      else
      {
        bRetValue = IDRS_FALSE;
      }
    }
  }

  return bRetValue;
}

/*
 *
 */
IDRS_BOOL CSampleSetup::ReadSampleSetupInfo ( )
{
  FILE * pFile;

  IDRS_BOOL bRetValue = IDRS_FALSE;

  // try to open the file containing the license information
  pFile = fopen ( m_strLicenseFilePath, "rb" );
  if ( pFile != NULL )
  {
    // read the license type
    if (fread(&m_ltLicenseType, sizeof(IDRS_LICENSE_TYPE), 1, pFile) > 0)
    {
      if (ReadLicenseInfo(pFile, m_objLicenseBarcode, m_bLoadBCode) && 
        ReadLicenseInfo(pFile, m_objLicenseOcr, m_bLoadOcr) &&
        ReadLicenseInfo(pFile, m_objLicenseDocumentOutput, m_bLoadDocumentOutput) &&
        ReadLicenseInfo(pFile, m_objLicenseDocumentOutputLite, m_bLoadDocumentOutputLite) &&
        ReadLicenseInfo(pFile, m_objLicenseImageFile, m_bLoadImageFile) && 
        ReadLicenseInfo(pFile, m_objLicensePrepro, m_bLoadPrepro))
      {
        bRetValue = IDRS_TRUE;
      }
      else
      {
        bRetValue = IDRS_FALSE;
      }
    }
    else
    {
      bRetValue = IDRS_FALSE;
    }

    fclose (pFile);
  }

  return bRetValue;
}

/*
 *  
 */
IDRS_BOOL CSampleSetup::Write(FILE * fp, IDRS_CSTR str, IDRS_UINT32 uiSize)
{
  IDRS_BOOL bRetValue = IDRS_FALSE;

  if (fp != NULL)
  {
    // allocate memory for the buffer and initialize it with 0
    IDRS_CHAR * pstrBuffer = new IDRS_CHAR[uiSize];
    memset(pstrBuffer, 0, uiSize * sizeof(IDRS_CHAR));

    // string copy with max uiSize characters
    strncpy(pstrBuffer, str, uiSize);

    // write text to file
    bRetValue = fwrite(pstrBuffer, sizeof(IDRS_CHAR), uiSize, fp) == uiSize * sizeof(IDRS_CHAR) ? IDRS_TRUE : IDRS_FALSE;

    // free memory allocated for the buffer
    delete []pstrBuffer;
  }

  return bRetValue;
}

/*
 *  
 */
IDRS_BOOL CSampleSetup::WriteLicenseInfo(FILE* fp, const CIDRSLicense& argLicense, const IDRS_BOOL bLoadLicense)
{
  IDRS_BOOL bRetValue = IDRS_FALSE;
  if (Write(fp, bLoadLicense))
  {
    bRetValue = IDRS_TRUE;
    if (bLoadLicense)
    {
      if (Write(fp, argLicense.GetModule()) &&
        Write(fp, argLicense.GetLicenseType()) &&
        Write(fp, argLicense.GetSoftwareKey(), IDRS_LICENSE_MAX_SIZE) &&
        Write(fp, argLicense.GetExtensionCount()))
      {
        // write information about extensions: enabled, key (if enabled)
        for (IDRS_UINT32 uiIndex = 0; uiIndex < argLicense.GetExtensionCount(); uiIndex++)
        {
          IDRS_EXTENSION eExtension = argLicense.GetExtensionAt ( uiIndex );
          IDRS_UINT uiExtEnable = argLicense.IsExtensionEnabled ( eExtension ) == IDRS_TRUE ? 1 : 0;
          if (Write(fp, uiExtEnable) == IDRS_TRUE)
          {
            if ( uiExtEnable )
            {
              if ( Write ( fp, argLicense.GetExtensionSoftwareKey ( eExtension ), IDRS_LICENSE_MAX_SIZE ) == IDRS_FALSE )
              {
                bRetValue = IDRS_FALSE;
                break;
              }
            }
          }
          else
          {
            bRetValue = IDRS_FALSE;
            break;
          }
        }
      }
      else
      {
        bRetValue = IDRS_FALSE;
      }
    }
  }

  return bRetValue;
}

/*
 *  
 */
IDRS_BOOL CSampleSetup::WriteLicenseInfo(FILE * fp, const CIDRSLicenseOcr& argLicense, const IDRS_BOOL bLoadLicense)
{
  IDRS_BOOL bRetValue = WriteLicenseInfo(fp, (const CIDRSLicense&)argLicense, bLoadLicense);
  if ((bRetValue) && (bLoadLicense))
  {
    IDRS_CHAR strOcrPath[IDRS_MAX_PATH] = {0};
    idrs_tchar2char(strOcrPath, argLicense.GetResourcesPath());

    bRetValue &= Write(fp, strOcrPath, IDRS_MAX_PATH);
  }

  return bRetValue;
}

/*
 *
 */
IDRS_INT CSampleSetup::WriteSampleSetupInfo ( )
{
  FILE * hFile = NULL;
  IDRS_INT iRetValue = -1;

  hFile = fopen ( m_strLicenseFilePath, "wb" );
  if ( hFile != NULL )
  {
    if (Write(hFile, m_ltLicenseType) && 
      WriteLicenseInfo(hFile, m_objLicenseBarcode, m_bLoadBCode) &&
      WriteLicenseInfo(hFile, m_objLicenseOcr, m_bLoadOcr) &&
      WriteLicenseInfo(hFile, m_objLicenseDocumentOutput, m_bLoadDocumentOutput) &&
      WriteLicenseInfo(hFile, m_objLicenseDocumentOutputLite, m_bLoadDocumentOutputLite) &&
      WriteLicenseInfo(hFile, m_objLicenseImageFile, m_bLoadImageFile) && 
      WriteLicenseInfo(hFile, m_objLicensePrepro, m_bLoadPrepro))
    {
      iRetValue = 0;
    }

    fclose ( hFile );
  }
  return iRetValue;
}
