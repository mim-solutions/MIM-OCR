/*
 * This sample code is a part of the IRIS iDRS library.
 * Copyright (C) 2006-2022 Image Recognition Integrated Systems, MiM Solutions Sp. z o.o.
 * All rights reserved.
 *
 */

#if defined(WIN32) || defined(WIN64)
#include <tchar.h>
#endif // WIN32

#include <iostream>
#include "CSampleSetup.h"
#include "CApplicationOptions.h"
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <codecvt>
#include <locale>

using namespace std;

/**
 *
 */
void ShowException ( const IDRS::CIDRSException & argIDRSException )
{
  cerr << "An error occurred in the iDRS." << endl;
  cerr << "Code " << argIDRSException.m_code << endl;
  cerr << "File " << argIDRSException.m_strSrcFile << endl;
  cerr << "Line " << argIDRSException.m_uiSrcLine << endl;

  switch ( argIDRSException.m_code )
  {
    case IDRS_ERROR_FILE_OPEN:
      cerr << "Unable to load the specified file. Please check its path." << endl;
      break;
    case IDRS_ERROR_IMAGE_TOO_LARGE:
      cerr << "The number of pixels in the supplied image size exceeds the maximum allowed value." << endl;
      break;
  }
}

/**
 * The COutput class illustrates how to create a specific parser.
 *
 * It saves the content of the zones to an HTML file using the reading order.
 *
 */
class COutput
{
public:
  //
  COutput ()
  {
    m_hFile = NULL;
  };
  //
  virtual ~COutput ()
  {
    /* Close the file if necessary */

    if ( m_hFile )
    {
      CloseFile ();
    }
  };
  /**
   * OpenFile opens the output file.
   */
  void OpenFile ( IDRS_CTSTR strOutputFilePath )
  {
    if ( m_hFile )
    {
      CloseFile ();
    }

    m_hFile = idrs_tfopen ( strOutputFilePath, idrs_t("wb"));
    if ( m_hFile == NULL )
    {
      idrs_tfprintf ( stderr, idrs_t ( "Unable to create %s\n" ), strOutputFilePath );
      ThrowException ( IDRS_ERROR_FILE_OPEN ); 
    }
  }

  /**
   * Export info about a word
   */
  void PrintWord( const CPageWord & objPageWord)
  {
    CPolygon objWordPolygon = objPageWord.GetBoundingPolygon();
    if (not objWordPolygon.IsRectangle())
    {
      return;
    }
    fprintf ( m_hFile, "            {\n");
    IDRS_RECT objWordRectangle = objWordPolygon.GetBoundingRect();
    fprintf ( m_hFile, "              \"left\": %d,\n", objWordRectangle.uiLeft);
    fprintf ( m_hFile, "              \"top\": %d,\n", objWordRectangle.uiTop);
    fprintf ( m_hFile, "              \"right\": %d,\n", objWordRectangle.uiRight);
    fprintf ( m_hFile, "              \"bottom\": %d,\n", objWordRectangle.uiBottom);

    CPageTextElementArray xTextElements = objPageWord.GetTextElements();
      IDRS_UINT uiTextElementsCount = xTextElements.GetCount();

    fprintf ( m_hFile, "              \"idrs_text_elements\": [\n");
    for (IDRS_UINT uiTextElemIndex = 0; uiTextElemIndex < uiTextElementsCount; uiTextElemIndex++)
    {
      CPageTextElement objTextElement = xTextElements.GetAt(uiTextElemIndex);
      PrintTextElement(objTextElement);
    }
    fprintf ( m_hFile, "              ]\n");
    fprintf ( m_hFile, "            },\n");
  }

  void PrintTextElementStyle( const CPageStyleTextElement & objTextElementStyle)
  {
    CPageStyleFont objTextElementFontStyle = objTextElementStyle.GetFontStyle();
    fprintf( m_hFile, "                  \"style\": {\n");
    fprintf( m_hFile, "                    \"font_size\": %d,\n", objTextElementFontStyle.GetFontSize());
    fprintf( m_hFile, "                    \"font_name\": \"%s\",\n", objTextElementFontStyle.GetPageFont().GetFontFamilyName());
    fprintf( m_hFile, "                    \"font_stretch\": %d,\n", objTextElementFontStyle.GetFontStretch());
    fprintf( m_hFile, "                    \"bold\": %d,\n", objTextElementStyle.GetIsBold());
    fprintf( m_hFile, "                    \"italic\": %d,\n", objTextElementStyle.GetIsItalic());
    fprintf( m_hFile, "                    \"underline\": %d,\n",objTextElementStyle.GetIsUnderlined());
    fprintf( m_hFile, "                    \"subscript\": %d,\n", objTextElementStyle.GetIsSubscript());
    fprintf( m_hFile, "                    \"superscript\": %d\n", objTextElementStyle.GetIsSuperscript());
    fprintf( m_hFile, "                  },\n");
  }


  /**
   * Add information for a text line
   */
  void AddLine( const CPageTextLine & argTextLine )
  {
    CPolygon objLinePolygon =  argTextLine.GetBoundingPolygon();
    if (not objLinePolygon.IsRectangle())
    {
      return;
    }
    fprintf ( m_hFile, "        {\n");
    IDRS_RECT objLineRectangle = objLinePolygon.GetBoundingRect();
    fprintf ( m_hFile, "          \"left\": %d,\n", objLineRectangle.uiLeft);
    fprintf ( m_hFile, "          \"top\": %d,\n", objLineRectangle.uiTop);
    fprintf ( m_hFile, "          \"right\": %d,\n", objLineRectangle.uiRight);
    fprintf ( m_hFile, "          \"bottom\": %d,\n", objLineRectangle.uiBottom);
    fprintf ( m_hFile, "          \"idrs_words\": [\n");

    const CPageWordArray xWords = argTextLine.GetWords();
    const IDRS_UINT uiWordsCount = xWords.GetCount();
    for (IDRS_UINT uiWordIndex = 0; uiWordIndex < uiWordsCount; uiWordIndex++)
    {
      CPageWord objPageWord = xWords.GetAt(uiWordIndex);
      PrintWord(objPageWord);
    }
    fprintf ( m_hFile, "          ]\n");
    fprintf ( m_hFile, "        },\n");

  }

  /**
   * Add information for a text zone
   */
  void AddTextZone( const CPageZoneText & argTextZone )
  {
    CPageParagraphsGroupArray xGroups = argTextZone.GetParagraphsGroups();
    for (IDRS_UINT uiGroupIndex = 0; uiGroupIndex < xGroups.GetCount(); uiGroupIndex++)
    {
      CPageParagraphsGroup objGroup = xGroups[uiGroupIndex];
      CPageParagraphArray xParags = objGroup.GetParagraphs();
      for (IDRS_UINT uiParagIndex = 0; uiParagIndex < xParags.GetCount(); uiParagIndex++)
      {
        CPageParagraph objParag = xParags[uiParagIndex];
        CPageTextLineArray xLines = objParag.GetTextLines();
        IDRS_UINT uiLinesCount = xLines.GetCount();
        for (IDRS_UINT uiLineIndex = 0; uiLineIndex < uiLinesCount; uiLineIndex++)
        {
          AddLine(xLines[uiLineIndex]);
        }
      }
    }
  }

  /**
   * Computes border css style
   */
  string GetBorderString(const IDRS_BOOL bEnabled, const string & strBorderType, IDRS_UINT32 uiBorderWidth, const IDRS_COLOR clrBorderColor)
  {
    char strTemp[200] = {0};

    if (bEnabled == IDRS_TRUE)
    {
      sprintf(strTemp, " border-%s:%dpx solid %s;", strBorderType.c_str(), uiBorderWidth, GetHTMLColorCode(clrBorderColor).c_str());
    }

    return strTemp;
  }

  /**
   * Computes padding css style
   */
  string GetPadding(const string & strDirection, IDRS_UINT32 uiValue)
  {
    char strTemp[200] = {0};
    sprintf(strTemp, " padding-%s: %d;", strDirection.c_str(), uiValue);
    return strTemp;
  }

  /**
   * Computes color code in HTML format
   */
  string GetHTMLColorCode(const IDRS_COLOR clrColor)
  {
    char strTemp[10] = {0};
    sprintf(strTemp, "#%02x%02x%02x", clrColor.ucRed, clrColor.ucGreen, clrColor.ucBlue);

    return strTemp;
  }

  /**
   * Computes style information: css, horizontal alignment & vertical alignment
   */
  string GetStyleInformation(const CPageStyleTableCell & argStyleTableCell)
  {
    const IDRS_CSTR xValuesAlign[] = {"", "left", "right", "justify", "center", "char"};
    const IDRS_CSTR xValuesValign[] = {"", "top", "middle", "bottom", "baseline"};

    string strStyle = "";

    // add borders
    string strStyleCSS = "";
    strStyleCSS += GetBorderString(argStyleTableCell.GetBottomBorder(), "bottom", argStyleTableCell.GetBottomBorderWidth(), argStyleTableCell.GetBottomBorderColor());
    strStyleCSS += GetBorderString(argStyleTableCell.GetLeftBorder(), "left", argStyleTableCell.GetLeftBorderWidth(), argStyleTableCell.GetLeftBorderColor());
    strStyleCSS += GetBorderString(argStyleTableCell.GetRightBorder(), "right", argStyleTableCell.GetRightBorderWidth(), argStyleTableCell.GetRightBorderColor());
    strStyleCSS += GetBorderString(argStyleTableCell.GetTopBorder(), "top", argStyleTableCell.GetTopBorderWidth(), argStyleTableCell.GetTopBorderColor());

    // add left & right padding
    strStyleCSS += GetPadding("left", argStyleTableCell.GetLeftPadding());
    strStyleCSS += GetPadding("right", argStyleTableCell.GetRightPadding());

    // add background-color
    strStyleCSS += " background-color:";
    strStyleCSS += GetHTMLColorCode(argStyleTableCell.GetBackgroundColor());
    strStyleCSS += ";";

    strStyle += "style=\"";
    strStyle += strStyleCSS;
    strStyle += "\"";

    // add horizontal alignment
    if (argStyleTableCell.GetHorizontalAlignment() < 6 && argStyleTableCell.GetHorizontalAlignment() > 0)
    {
      strStyle += " align=\"";
      strStyle += xValuesAlign[argStyleTableCell.GetHorizontalAlignment()];
      strStyle += "\"";
    }

    // add vertical alignment
    if (argStyleTableCell.GetVerticalAlignment() < 5 && argStyleTableCell.GetVerticalAlignment() > 0)
    {
      strStyle += " valign=\"";
      strStyle += xValuesValign[argStyleTableCell.GetVerticalAlignment()];
      strStyle += "\"";
    }

    return strStyle;
  }

  /**
   * Writes HTML table based on the supplied CPageZoneTable
   */
  void AddTableZone( const CPageZoneTable & argTableZone )
  {
    // add the collapsing borders model, use collapse to make borders are collapsed into a single border

    CPageTableCellArray xCells = argTableZone.GetCells();
    const IDRS_UINT uiCellsCount = xCells.GetCount();
    IDRS_INT iCurrentRowIndex = -1;

    for (IDRS_UINT uiCellIndex = 0; uiCellIndex < uiCellsCount; uiCellIndex++)
    {
      CPageTableCell objCell = xCells.GetAt(uiCellIndex);

      if ( iCurrentRowIndex == -1)
      {
        iCurrentRowIndex = objCell.GetRowIndex();
      }
      else if ( iCurrentRowIndex != objCell.GetRowIndex() )
      {
        iCurrentRowIndex = objCell.GetRowIndex();
      }

      string strStyle = GetStyleInformation( objCell.GetCellStyle() );

      CPageTextLineArray xTextLines = objCell.GetTextLines();
      const IDRS_UINT uiTextLinesCount = xTextLines.GetCount();
      for (IDRS_UINT uiLineIndex = 0; uiLineIndex < uiTextLinesCount; uiLineIndex++)
      {
        AddLine(xTextLines.GetAt(uiLineIndex));
      }
    }
  }

  /**
   * AddBarcode
   */
  void AddBarcodeZone( const CPageZoneBarcode & argBarcodeZone )
  {
    /* To deal with barcode zone take a look at the CppBarcode sample*/
  }

  /**
   * AddZone
   */
  void AddZone( const CPageZone & argZone )
  {
    switch (argZone.GetZoneType())
    {
    case IDRS_ZONE_TABLE:
    {
      CPageZoneTable objTableone(argZone);
      AddTableZone(objTableone);
    }
    break;
    case IDRS_ZONE_TEXT:
    {
      CPageZoneText objTextZone(argZone);
      AddTextZone(objTextZone);
    }
    break;
    case IDRS_ZONE_BARCODE:
    {
      CPageZoneBarcode objBarcodeZone(argZone);
      AddBarcodeZone(objBarcodeZone);
    }
    break;
    case IDRS_ZONE_GRAPHIC:
    case IDRS_ZONE_HAND:
      break;
    }
  }
  /**
   * AddPage output the page the HTML file.
   */
  void AddPage ( const CPageContent2 & argPageContent2 )
  {
    if ( m_hFile == NULL )
    {
      return;
    }
    fprintf ( m_hFile, "{\n  \"idrs_pages\": [\n");
    fprintf ( m_hFile, "    {\n      \"idrs_lines\": [\n");

    CPageSection2Array xSections = argPageContent2.GetSections();
    const IDRS_UINT uiSectionsCount = xSections.GetCount();

    for (  IDRS_UINT32 uiSectionIndex = 0; uiSectionIndex < uiSectionsCount; uiSectionIndex++ )
    {
      CPageSection2 objSection = xSections.GetAt(uiSectionIndex);

      CPageColumnArray xColumns = objSection.GetColumns();
      const IDRS_UINT uiColumnsCount = xColumns.GetCount();

      for (IDRS_UINT uiColumnIndex = 0; uiColumnIndex < uiColumnsCount; uiColumnIndex++)
      {
        CPageColumn objColumn = xColumns.GetAt(uiColumnIndex);

        CPageZoneArray xZones = objColumn.GetZones();
        const IDRS_UINT uiZonesCount = xZones.GetCount();

        for (IDRS_UINT32 uiZoneIndex = 0; uiZoneIndex < uiZonesCount; uiZoneIndex++)
        {
          AddZone(objColumn.GetZones()[uiZoneIndex]);
        }
      }

      CPageZoneArray xZones = objSection.GetZones();
      const IDRS_UINT uiZonesCount = xZones.GetCount();

      for (IDRS_UINT32 uiZoneIndex = 0; uiZoneIndex < uiZonesCount; uiZoneIndex++)
      {
        AddZone(argPageContent2.GetSections()[uiSectionIndex].GetZones()[uiZoneIndex]);
      }
    }
    fprintf ( m_hFile, "      ]\n    }\n");
    fprintf ( m_hFile, "  ]\n}\n");
  }
  /**
   * CloseFile closes the JSON file.
   */
  void CloseFile ()
  {
    if ( m_hFile == NULL )
      return;
    fclose ( m_hFile );
    m_hFile = NULL;
  }
  void PrintTextElement(const CPageTextElement & argTextElement)
  {
    fprintf(m_hFile, "                {\n");
    fprintf(m_hFile, "                  \"confidence\": %d,\n", argTextElement.GetConfidenceLevel());
    fprintf(m_hFile, "                  \"idrs_characters\": [\n");
    IDRS_UINT uiIndex = 0;
    IDRS_WCHAR wCh;
    while (( wCh = (argTextElement.GetTextValue() [ uiIndex ]) ) != 0 )
    {
      uiIndex ++;
      fprintf ( m_hFile, "                    %d,\n", wCh);
    }
    fprintf( m_hFile, "                  ],\n");

    CPageStyleTextElement textElementStyle = argTextElement.GetStyle();
    PrintTextElementStyle(textElementStyle);

    fprintf(m_hFile, "                  \"alternatives\": [\n");
    CPageTextElementAlternativeArray alternatives = argTextElement.GetAlternatives();
    IDRS_UINT aternativesCount = alternatives.GetCount();
    for (IDRS_UINT alternativeIndex = 0; alternativeIndex < aternativesCount; alternativeIndex++)
    {
      fprintf(m_hFile, "                    {\n");
      CPageTextElementAlternative alternative = alternatives.GetAt(alternativeIndex);
      fprintf(m_hFile, "                      \"confidence\": %d,\n", alternative.GetConfidenceLevel());
      const IDRS_WCHAR * alternativeSolution = alternative.GetSolution();
      IDRS_UINT altIndex = 0;
      IDRS_WCHAR aCh;
      fprintf(m_hFile, "                      \"idrs_characters\": [\n");
      while (( aCh = (alternativeSolution[altIndex]) ) != 0 ){
      fprintf(m_hFile, "                        %d,\n", aCh);
        altIndex++;
      }

      fprintf(m_hFile, "                      ]\n");
      fprintf(m_hFile, "                    },\n");
    }
    fprintf(m_hFile, "                  ]\n");
    fprintf(m_hFile, "                },\n");
  }
private:
  /**
   * The output file.
   */
  FILE * m_hFile;
  int box_id=0;

};

/**
 *
 */
void PrintUsage ()
{
  cout << "Usage:" << endl;
  cout << "CppImage2Jsoml16 [options] -input image.tif -output output.json" << endl;
  cout << "Valid options:" << endl;
  cout << "-detect_orientation (optional)\n  Enables text orientation detection" << endl;
  cout << "-deskew (optional)\n  Enables skew correction" << endl;
  cout << "-smoothing (optional)\n  Enables image smoothing" << endl;
  cout << "-adaptive (optional)\n  Enables adaptive binarization" << endl;
  // cout << "-perspective (optional)\n  Enables perspective correction" << endl;
  cout << "-language [language identifier]  (optional)\n  Specify the recognition language (17 for polish)" << endl;
  cout << "-licence [licence_file_path]  (optional)\n  Specify path to licence file" << endl;
  cout << "-lexicon [custom_lexicon_path]  (optional)\n  Specify path to file with additional words to add to lexicon." << endl;
  cout << "-output-image [output path for preprocessed image]\n  Specify path to file where preprocessed image should be saved." << endl;
  cout << "Examples:" << endl;
  cout << "CppImage2Json16 -input image.tif -output output.json" << endl;
  cout << "CppImage2Json16 -language 17 -input image.tif -output output.json -output-image preprocessed_image.png" << endl;
  cout << "CppImage2Json16 -detect_orientation -deskew -language 0 -input image.tif -output output.json -licence licence_file" << endl;
}

/**
 * Prints program information
 */
void PrintProgramInformation ()
{
  fprintf ( stdout, "The CppImage2Json16 program is a console application performing image preprocessing and OCR recognition.\n");
  fprintf ( stdout, "Result is saved into Json-like file format readable by mim-ocr Box object\n");
}

/**
 * Application entry point.
 *
 */
#if defined(WIN32) || defined(WIN64)
int _tmain( int argc, _TCHAR * argv[] )
#else // WIN32 || WIN64
int main ( int argc, char * argv [] )
#endif // WIN32 || WIN64
{

//  CSampleSetup objSampleSetup;
  bool bIsReady;
  //! Input image buffer
  IDRS_TCHAR strInputImage [ IDRS_MAX_PATH ];
  //! Output file buffer
  IDRS_TCHAR strOutputFile [ IDRS_MAX_PATH ];
  IDRS_TCHAR strLicenceFile [ IDRS_MAX_PATH ];
  IDRS_TCHAR strLexiconFile [ IDRS_MAX_PATH ];
  IDRS_TCHAR strOutputImage [ IDRS_MAX_PATH ];

  PrintProgramInformation();

  CApplicationOptions objApplicationOptions(argc, (IDRS_CTSTR*)argv);

  if (objApplicationOptions.ValidArguments() == IDRS_FALSE)
  {
    PrintUsage ();
    return EXIT_FAILURE;
  }

  // get the input image path & output file path
  objApplicationOptions.GetInputImage(strInputImage, IDRS_MAX_PATH);
  objApplicationOptions.GetOutputFile(strOutputFile, IDRS_MAX_PATH);
  objApplicationOptions.GetLicenceFile(strLicenceFile, IDRS_MAX_PATH);
  objApplicationOptions.GetLexiconFile(strLexiconFile, IDRS_MAX_PATH);
  objApplicationOptions.GetOutputImage(strOutputImage, IDRS_MAX_PATH);
    
  /*
   * Sets up the iDRS and checks the state of the IDRS_MODULE_OCR and IDRS_MODULE_PREPRO modules.
   */
   CSampleSetup objSampleSetup(strLicenceFile);

  try
  {
    if ( objSampleSetup.SetupIDRS() == IDRS_FALSE )
    {
      cerr << "Unable to setup iDRS.\n" << endl;
      return - 1;
    }
    else
    {
      bIsReady = true;
    }
  }
  catch ( CIDRSException & objIDRSException )
  {
    CIDRSSetup::Unload ();
    ShowException ( objIDRSException );
    return EXIT_FAILURE;
  }

  /* Check the loaded modules */

  try
  {
    if ( ! CIDRSSetup::IsModuleReady ( IDRS_MODULE_OCR ))
    {
      cerr << "ERROR - This sample requires the IDRS_MODULE_OCR module to work." << endl;
      bIsReady = false;
    }

    if ( ! CIDRSSetup::IsModuleReady ( IDRS_MODULE_PREPRO ))
    {
      cerr << "ERROR - This sample requires the IDRS_MODULE_PREPRO module to work.\n" << endl;
      bIsReady = false;
    }
  }
  catch ( const CIDRSException & objIDRSException )
  {
    bIsReady = false;
    ShowException ( objIDRSException );
  }

  if ( ! bIsReady )
  {
    CIDRSSetup::Unload ();
    return EXIT_FAILURE;
  }

  try
  {
    CPage objPage;
    CPageRecognition objPageRecognition;
    CIDRS objIDRS;
    COcrContext objOCRContext;
    CStopwatch objStopwatchTotal, objStopwatchLoad, objStopwatchRead;

    /*
     * Initializes the OCR context and the reader.
     */

    objIDRS = CIDRS::Create();

    objPageRecognition = CPageRecognition::Create ( objIDRS );

    objOCRContext = COcrContext::Create ( objApplicationOptions.GetLanguage ());

    if ( strLexiconFile[0] != 0 )
    {
      objOCRContext.SetUserLexicon( strLexiconFile );
    }

    objPageRecognition.SetContext ( objOCRContext );

    objPageRecognition.SetOrientationDetection ( objApplicationOptions.GetDetectionOrientation (), IDRS_TRUE );

    CBinarizeOptions objBinarizeOptions = objPageRecognition.GetBinarizationOptions ();
    // We always keep preprocessed image. For strange reasons it improves OCR results.
    objBinarizeOptions.SetKeepBinarizedImage ( IDRS_TRUE );

    // if adaptive algorithm and smoothing should be used 
    objBinarizeOptions.SetAutoAdjust ( objApplicationOptions.GetAdaptiveBinarization() );
    objBinarizeOptions.SetSmoothing ( objApplicationOptions.GetSmoothing () );

    objPageRecognition.SetBinarizationOptions ( objBinarizeOptions );

    /*
     * Create the page, load the image and preprocess
     */

    objStopwatchTotal = IDRS::CStopwatch::Create ();
    objStopwatchLoad = IDRS::CStopwatch::Create ();
    objStopwatchRead = IDRS::CStopwatch::Create ();

    objStopwatchTotal.Start ();
    objStopwatchLoad.Start ();

    objPage = CPage::Create ( objIDRS );
    objPage.LoadSourceImage ( strInputImage );
    
    // apply deskew correction, if requested
    if ( objApplicationOptions.GetDeskew ())
    {
      CDeskew objDeskew = CDeskew::Create ( objIDRS );
      objDeskew.Deskew ( objPage );
    }

    // apply perspective correction, if requested
    if ( objApplicationOptions.GetPerspectiveCorrection ())
    {
      CImageSource objImageSourceDetection = CImageSource::Create ( objIDRS );
      if ( objImageSourceDetection.GetSourceType ( objPage ) != CImageSource::SCANNER )
      {
        CPerspective objPerspective = CPerspective::Create ( objPage );
        IDRS_PERSPECTIVE_CORNERS pcCorners = objPerspective.GetCorners ();
        objPerspective.Correct ( pcCorners );
      }
    }

    objStopwatchLoad.Stop ();

    /*
     * Recognize the image
     */

    objStopwatchRead.Start ();
    objPageRecognition.RecognizePage ( objPage );
    objStopwatchRead.Stop ();

    objStopwatchTotal.Stop ();

    IDRS_UINT
      uiHour, uiMinute, uiSecond, uiMilliseconds;

    objStopwatchTotal.GetElapsedTime ( uiHour, uiMinute, uiSecond, uiMilliseconds );
//    cout << "Total elapsed time: " << uiMinute << "m " << uiSecond << "s " << uiMilliseconds << "ms" << endl;

    objStopwatchLoad.GetElapsedTime ( uiHour, uiMinute, uiSecond, uiMilliseconds );
//    cout << "File loading: " << uiMinute << "m " << uiSecond << "s " << uiMilliseconds << "ms" << endl;

    objStopwatchRead.GetElapsedTime ( uiHour, uiMinute, uiSecond, uiMilliseconds );
//    cout << "Reading: " << uiMinute << "m " << uiSecond << "s " << uiMilliseconds << "ms" << endl;

    /*
     * save preprocessed image
     */
    if ( strOutputImage[0] !=  0 ) {
      cout << "Saving preprocessed image to: " << strOutputImage << endl;
      CImageOptions objImageOptions = CImageOptions::Create ( IDRS::CImageFileFormat::IDRS_PNG );
      objPage.SaveBlackAndWhiteImage ( strOutputImage, IDRS::CImageFileFormat::IDRS_PNG, objImageOptions );
    }
    
    /*
     * Create the OCR output
     */
    COutput objOutput;

    objOutput.OpenFile ( strOutputFile );    
    CPageContent2 objPageContent2 = objPage.GetPageContent2();
    objOutput.AddPage ( objPageContent2 );
  }
  catch ( const IDRS::CIDRSException & objIDRSException )
  {
    ShowException ( objIDRSException );
    IDRS::CIDRSSetup::Unload ();
    return EXIT_FAILURE;
  }

  IDRS::CIDRSSetup::Unload ();
  return EXIT_SUCCESS;
}
