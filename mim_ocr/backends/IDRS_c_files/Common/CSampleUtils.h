/*
 * This sample code is a part of the IRIS iDRS library.
 * Copyright (C) 2006-2022 Image Recognition Integrated Systems
 * All rights reserved.
 *
 * This source code is merely intended as a supplement to the iDRS reference and the electronic documentation provided with the library.
 *
 */

#include <idrs.h>

using namespace IDRS;

/**
 * \brief Class CSampleUtils provides basic utility methods to iDRS samples.
 */
class CSampleUtils
{
public:
  /**
   * \brief Get user's anwser of the question, as a boolean.
   * \param strQuestion The question to be asked
   * \return The answer provided.
   */
  static inline IDRS_BOOL GetBoolean ( IDRS_CSTR strQuestion );
  /**
   * \brief Get user's anwser of the question, as an unsigned char.
   * \param strQuestion The question to be asked
   * \return The answer provided.
   */
  static inline IDRS_UCHAR GetUnsignedChar ( IDRS_CSTR strQuestion );
  /**
   * \brief Get user's anwser of the question, as an unsigned integer.
   * \param strQuestion The question to be asked
   * \return The answer provided.
   */
  static inline IDRS_UINT GetUnsignedInteger ( IDRS_CSTR strQuestion );
  /**
   * \brief Read a string from the stdin and store it in the given buffer.
   *
   * \param strBuffer the buffer to store to
   * \param uiBufferSize the size of the buffer
   * \return IDRS_TRUE if the string is entirely contained in the provided buffer, IDRS_FALSE if the string was too long or if an error occured while reading it
   * \note even if the string was longer than the buffer, it will still be consumed so that next calls are not affected.
   */
  static inline IDRS_BOOL GetString ( IDRS_STR strBuffer, IDRS_UINT uiBufferSize );
  /**
   * \brief Print out the menu title.
   * \param strMenuTitle The title of the menu
   */
  static inline void StartNewMenu ( IDRS_CSTR strMenuTitle );
  /**
   * \brief Display the details of an iDRS exception.
   * \param argIDRSException The iDRS exception to display
   */
  static inline void ShowException ( const CIDRSException & argIDRSException );
};
/*
 *
 */
inline IDRS_BOOL CSampleUtils::GetBoolean ( IDRS_CSTR strQuestion )
{
  return GetUnsignedChar ( strQuestion ) == 'y' ? IDRS_TRUE : IDRS_FALSE;
}
/*
 *
 */
inline IDRS_UCHAR CSampleUtils::GetUnsignedChar ( IDRS_CSTR strQuestion )
{
  printf ( "%s", strQuestion );
  IDRS_CHAR str [ 2 ];
  GetString ( str, 2 );
  return str [ 0 ];
}
/*
 *
 */
inline IDRS_UINT CSampleUtils::GetUnsignedInteger ( IDRS_CSTR strQuestion )
{
  printf ( "%s", strQuestion );
  char str [ IDRS_MAX_PATH ];
  GetString ( str, IDRS_MAX_PATH );
  return ( IDRS_UINT ) atoi ( str );
}
/*
 *
 */
inline IDRS_BOOL CSampleUtils::GetString ( IDRS_STR strBuffer, IDRS_UINT uiBufferSize )
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
inline void CSampleUtils::StartNewMenu ( IDRS_CSTR strMenuTitle )
{
  unsigned int ui, uiLength;

  uiLength = ( unsigned int ) strlen ( strMenuTitle ) + 4;

  for ( ui = 0; ui < uiLength; ui ++ )
  {
    printf ( "*" );
  }

  printf ( "\n* %s *\n", strMenuTitle );

  for ( ui = 0; ui < uiLength; ui ++ )
  {
    printf ( "*" );
  }

  printf ( "\n" );
}
/*
 *
 */
inline void CSampleUtils::ShowException ( const CIDRSException & argIDRSException )
{
  // Provide general details: Code, File and line
  printf ( "An error occurred in the iDRS.\n" );
  printf ( "Code %lu\n", argIDRSException.m_code );
  printf ( "File %s\n", argIDRSException.m_strSrcFile );
  printf ( "Line %u\n", argIDRSException.m_uiSrcLine );
  // Provide a more complete description for the most frequent errors
  switch ( argIDRSException.m_code )
  {
    case IDRS_ERROR_INVALID_ARGS:
      fprintf ( stderr, "The set of parameters provided is not supported. Please check the parameters.\n" );
      break;
    case IDRS_ERROR_FILE_OPEN:
      fprintf ( stderr, "Unable to load the specified file. Please check its path.\n" );
      break;
    case IDRS_ERROR_NO_IMAGING_MODULE_READY:
      fprintf ( stderr, "No imaging module is ready. An imaging module is necessary to load/save image files.\n" );
      break;
    case IDRS_ERROR_CHARACTER_RECOGNITION_ENGINE_NO_ASIAN_READY:
      fprintf ( stderr, "No Asian OCR add-on is ready.\n" );
      break;
    case IDRS_ERROR_CHARACTER_RECOGNITION_ENGINE_HEBREW_NOT_READY:
      fprintf ( stderr, "The Hebrew OCR add-on is not ready.\n" );
      break;
    case IDRS_ERROR_CHARACTER_RECOGNITION_ENGINE_HAND_WRITE_NOT_READY:
      fprintf ( stderr, "The Hand write module is not ready.\n" );
      break;
    case IDRS_ERROR_CHARACTER_RECOGNITION_ENGINE_BANKING_FONTS_NOT_READY:
      fprintf ( stderr, "The banking fonts recognition add-on is not ready.\n" );
      break;
    case IDRS_ERROR_CHARACTER_RECOGNITION_ENGINE_ARABIC_NOT_READY:
      fprintf ( stderr, "The Arabic OCR add-on is not ready.\n" );
      break;
    case IDRS_ERROR_INVALID_IMAGE_INDEX:
        fprintf ( stderr, "Page loaded with invalid page index.\n" );
        break;
    case IDRS_ERROR_IMAGE_FILE_PDF_NOT_READY:
        fprintf ( stderr, "Imaging module Pdf extension is not enabled. Pdf extension is necessary to load pdf files.\n" );
        break;
    case IDRS_ERROR_IMAGE_TOO_LARGE:
        fprintf (stderr, "The number of pixels in the supplied image size exceeds the maximum allowed value.\n");
        break;
    case IDRS_ERROR_FAILURE:
      fprintf (stderr, "The function failed.\n");
      break;
  }
}
