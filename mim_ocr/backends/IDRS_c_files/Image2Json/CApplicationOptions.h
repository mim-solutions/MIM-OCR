/*
 * This sample code is a part of the IRIS iDRS library.
 * Copyright (C) 2006-2022 Image Recognition Integrated Systems
 * All rights reserved.
 *
 * This source code is merely intended as a supplement to the iDRS reference and the electronic documentation provided with the library.
 *
 */

/**
 * \brief CApplicationOptions is used to compute the CppImage2Html application command line options
 */
class CApplicationOptions
{
public:
  /**
   * \brief CApplicationOptions constructor analyzes the command line arguments and extracts the useful options
   *
   * \param uiArgCount Number of arguments
   * \param xArguments Array containing the arguments
   */
  inline CApplicationOptions(const IDRS_UINT uiArgCount, IDRS_CTSTR xArguments[]);
  /**
   * \brief GetDetectionOrientation retrieves the orientation detection option
   *
   * \return Flag indicating if orientation detection should be applied or not
   */
  inline IDRS_BOOL GetDetectionOrientation() const;
  /**
   * \brief GetDeskew retrieves the deskew option
   *
   * \return Flag indicating if deskew should be applied or not
   */
  inline IDRS_BOOL GetDeskew() const;
  /**
   * \brief GetPerspectiveCorrection retrieves the perspective correction option
   *
   * \return Flag indicating if perspective correction should be applied or not
   */
  inline IDRS_BOOL GetPerspectiveCorrection() const;
  /**
   * \brief GetSmoothing retrieves the smoothing option
   *
   * \return Flag indicating if image should be smoothed before recognition
   */
  inline IDRS_BOOL GetSmoothing() const;
  /**
   * \brief GetAddaptiveBinarization retrieves the smoothing option
   *
   * \return Flag indicating if adaptive binarization algorithm should be used
   */
  inline IDRS_BOOL GetAdaptiveBinarization() const;
  /**
   * \brief GetLanguage retrieves the language option
   *
   * \return Language identifier to be used for recognition
   */
  inline IDRS_LANGUAGE GetLanguage() const;
  /**
   * \brief GetInputImage copies the input image path to supplied buffer
   *
   * \param strOutputBuffer Buffer where to input image path should be copied
   * \param uiBufferSize Buffer size. If the input image path size exceeds this value, an exception will be thrown
   */
  inline void GetInputImage(IDRS_TSTR strOutputBuffer, const IDRS_UINT uiBufferSize) const;
  /**
   * \brief GetOutputFile copies the output file path to supplied buffer
   *
   * \param strOutputBuffer Buffer where to output file path should be copied
   * \param uiBufferSize Buffer size. If the input image path size exceeds this value, an exception will be thrown
   */
  inline void GetOutputFile(IDRS_TSTR strOutputBuffer, const IDRS_UINT uiBufferSize) const;
  /**
   * \brief GetLicenceFile copies the licence file path to supplied buffer
   *
   * \param strOutputBuffer Buffer where to output file path should be copied
   * \param uiBufferSize Buffer size. If the input image path size exceeds this value, an exception will be thrown
   */
  inline void GetLicenceFile(IDRS_TSTR strOutputBuffer, const IDRS_UINT uiBufferSize) const;
  /**
   * \brief GetLexiconFile copies the additional lexicon file path to supplied buffer
   *
   * \param strOutputBuffer Buffer where to output file path should be copied
   * \param uiBufferSize Buffer size. If the input image path size exceeds this value, an exception will be thrown
   */
  
  inline void GetLexiconFile(IDRS_TSTR strOutputBuffer, const IDRS_UINT uiBufferSize) const;
  /**
   * \brief GetOutputImage copies the preprocessed image file path to supplied buffer
   *
   * \param strOutputBuffer Buffer where to output file path should be copied
   * \param uiBufferSize Buffer size. If the input image path size exceeds this value, an exception will be thrown
   */ 
  inline void GetOutputImage(IDRS_TSTR strOutputBuffer, const IDRS_UINT uiBufferSize) const;
  
  inline IDRS_BOOL ValidArguments() const;
private:
  //! Detect orientation flag
  IDRS_BOOL m_bDetectOrientation;
  //! Deskew flag
  IDRS_BOOL m_bDeskew;
  //! Perspective correction flag
  IDRS_BOOL m_bPerspectiveCorrection;
  //! Smoothing flag
  IDRS_BOOL m_bSmoothing;
  //! Adaptive binarization flag
  IDRS_BOOL m_bAdaptiveBinarization;
  //! Language identifier
  IDRS_LANGUAGE m_lLanguage;
  //! Input image buffer
  IDRS_TCHAR m_strInputImage [ IDRS_MAX_PATH ];
  //! Output file buffer
  IDRS_TCHAR m_strOutputFile [ IDRS_MAX_PATH ];
  //! Licence file buffer
  IDRS_TCHAR m_strLicenceFile [ IDRS_MAX_PATH ];
  //! Lexicon file buffer
  IDRS_TCHAR m_strLexiconFile [ IDRS_MAX_PATH ];
  //! Preprocessed image file buffer
  IDRS_TCHAR m_strOutputImage [ IDRS_MAX_PATH ];
};
/*
 *
 */
inline CApplicationOptions::CApplicationOptions(const IDRS_UINT uiArgCount, IDRS_CTSTR xArguments[])
{
  IDRS_UINT iArgIndex = 1;
  m_bDetectOrientation = IDRS_FALSE;
  m_bDeskew = IDRS_FALSE;
  m_bSmoothing = IDRS_FALSE;
  m_bAdaptiveBinarization = IDRS_FALSE;
  m_bPerspectiveCorrection = IDRS_FALSE;
  m_lLanguage = IDRS_LNG_ENGLISH;
  m_strInputImage [ 0 ] = 0;
  m_strOutputFile [ 0 ] = 0;
  m_strLicenceFile [ 0 ] = 0;
  m_strLexiconFile [ 0 ] = 0;
  m_strOutputImage [ 0 ] = 0;

  while ( iArgIndex < uiArgCount )
  {
    if ( idrs_tcsequal ( xArguments [ iArgIndex ], idrs_t("-detect_orientation") ) == IDRS_TRUE )
    {
      m_bDetectOrientation = IDRS_TRUE;
      iArgIndex ++;
    }
    else if ( idrs_tcsequal ( xArguments [ iArgIndex ], idrs_t("-deskew") ) == IDRS_TRUE )
    {
      m_bDeskew = IDRS_TRUE;
      iArgIndex ++;
    }
    else if ( idrs_tcsequal ( xArguments [ iArgIndex ], idrs_t("-smoothing") ) == IDRS_TRUE )
    {
      m_bSmoothing = IDRS_TRUE;
      iArgIndex ++;
    }
    else if ( idrs_tcsequal ( xArguments [ iArgIndex ], idrs_t("-adaptive") ) == IDRS_TRUE )
    {
      m_bAdaptiveBinarization = IDRS_TRUE;
      iArgIndex ++;
    }
    else if ( idrs_tcsequal ( xArguments [ iArgIndex ], idrs_t("-perspective") ) == IDRS_TRUE )
    {
      m_bPerspectiveCorrection = IDRS_TRUE;
      iArgIndex ++;
    }
    else if ( idrs_tcsequal ( xArguments [ iArgIndex ], idrs_t("-language") ) == IDRS_TRUE )
    {
      iArgIndex ++;

      if ( iArgIndex < uiArgCount )
      {
        m_lLanguage = ( IDRS_LANGUAGE ) idrs_tcstol( xArguments [ iArgIndex ++ ], NULL, 10);
      }
    }
    else if ( idrs_tcsequal ( xArguments [ iArgIndex ], idrs_t("-input") ) == IDRS_TRUE )
    {
      iArgIndex ++;

      if ( iArgIndex < uiArgCount )
      {
        idrs_sntprintf(m_strInputImage, IDRS_MAX_PATH, xArguments [ iArgIndex ++ ]);
      }
    }
    else if ( idrs_tcsequal ( xArguments [ iArgIndex ], idrs_t("-output") ) == IDRS_TRUE )
    {
      iArgIndex ++;

      if ( iArgIndex < uiArgCount )
      {
        idrs_sntprintf(m_strOutputFile, IDRS_MAX_PATH, xArguments [ iArgIndex ++ ]);
      }
    }
    else if ( idrs_tcsequal ( xArguments [ iArgIndex ], idrs_t("-licence") ) == IDRS_TRUE )
    {
      iArgIndex ++;

      if ( iArgIndex < uiArgCount )
      {
        idrs_sntprintf(m_strLicenceFile, IDRS_MAX_PATH, xArguments [ iArgIndex ++ ]);
      }
    }
    else if ( idrs_tcsequal ( xArguments [ iArgIndex ], idrs_t("-lexicon") ) == IDRS_TRUE )
    {
      iArgIndex ++;

      if ( iArgIndex < uiArgCount )
      {
        idrs_sntprintf(m_strLexiconFile, IDRS_MAX_PATH, xArguments [ iArgIndex ++ ]);
      }
    }
    else if ( idrs_tcsequal ( xArguments [ iArgIndex ], idrs_t("-output-image") ) == IDRS_TRUE )
    {
      iArgIndex ++;

      if ( iArgIndex < uiArgCount )
      {
        idrs_sntprintf(m_strOutputImage, IDRS_MAX_PATH, xArguments [ iArgIndex ++ ]);
      }
    }
    else
    {
      // Unsupported argument: invalidate file paths then break the loop.
      m_strInputImage [ 0 ] = 0;
      m_strOutputFile [ 0 ] = 0;
      m_strLicenceFile [ 0 ] = 0;
      m_strLexiconFile [ 0 ] = 0;
      m_strOutputImage [ 0 ] = 0;
      break;
    }
  }
}
/*
 *
 */
inline IDRS_BOOL CApplicationOptions::GetDetectionOrientation() const
{
  return m_bDetectOrientation;
}
/*
 *
 */
inline IDRS_BOOL CApplicationOptions::GetDeskew() const
{
  return m_bDeskew;
}
/*
 *
 */
inline IDRS_BOOL CApplicationOptions::GetPerspectiveCorrection() const
{
  return m_bPerspectiveCorrection;
}
/*
 *
 */
inline IDRS_BOOL CApplicationOptions::GetSmoothing() const
{
  return m_bSmoothing;
}
/*
 *
 */
inline IDRS_BOOL CApplicationOptions::GetAdaptiveBinarization() const
{
  return m_bAdaptiveBinarization;
}
/*
 *
 */
inline IDRS_LANGUAGE CApplicationOptions::GetLanguage() const
{
  return m_lLanguage;
}
/*
 *
 */
inline void CApplicationOptions::GetInputImage(IDRS_TSTR strOutputBuffer, const IDRS_UINT uiBufferSize) const
{
  if (idrs_tcslen(m_strInputImage) <= uiBufferSize)
  {
    idrs_tcscpy(strOutputBuffer, m_strInputImage);
  }
  else
  {
    ThrowException(IDRS_ERROR_BUFFER_TOO_SMALL);
  }
}
/*
 *
 */
inline void CApplicationOptions::GetOutputFile(IDRS_TSTR strOutputBuffer, const IDRS_UINT uiBufferSize) const
{
  if (idrs_tcslen(m_strOutputFile) <= uiBufferSize)
  {
    idrs_tcscpy(strOutputBuffer, m_strOutputFile);
  }
  else
  {
    ThrowException(IDRS_ERROR_BUFFER_TOO_SMALL);
  }
}
/*
 *
 */
inline void CApplicationOptions::GetLicenceFile(IDRS_TSTR strOutputBuffer, const IDRS_UINT uiBufferSize) const
{
  if (idrs_tcslen(m_strLicenceFile) <= uiBufferSize)
  {
    idrs_tcscpy(strOutputBuffer, m_strLicenceFile);
  }
  else
  {
    ThrowException(IDRS_ERROR_BUFFER_TOO_SMALL);
  }
}
/*
 *
 */
inline void CApplicationOptions::GetLexiconFile(IDRS_TSTR strOutputBuffer, const IDRS_UINT uiBufferSize) const
{
  if (idrs_tcslen(m_strLexiconFile) <= uiBufferSize)
  {
    idrs_tcscpy(strOutputBuffer, m_strLexiconFile);
  }
  else
  {
    ThrowException(IDRS_ERROR_BUFFER_TOO_SMALL);
  }
}
/*
 *
 */
inline void CApplicationOptions::GetOutputImage(IDRS_TSTR strOutputBuffer, const IDRS_UINT uiBufferSize) const
{
  if (idrs_tcslen(m_strOutputImage) <= uiBufferSize)
  {
    idrs_tcscpy(strOutputBuffer, m_strOutputImage);
  }
  else
  {
    ThrowException(IDRS_ERROR_BUFFER_TOO_SMALL);
  }
}
/*
 *
 */
inline IDRS_BOOL CApplicationOptions::ValidArguments() const
{
  if ((idrs_tcslen(m_strInputImage) > 0) && (idrs_tcslen(m_strOutputFile) > 0))
  {
    return IDRS_TRUE;
  }

  return IDRS_FALSE;
}