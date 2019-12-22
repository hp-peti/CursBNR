using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace CursBNR
{
	static class Program
	{
		/// <summary>
		/// The main entry point for the application.
		/// </summary>
		[STAThread]
		static void Main()
		{
			try
			{
				TrendForm.LoadValues("bnr.xml");
			}
			catch(Exception x)
			{
				System.Diagnostics.Debug.Print(x.ToString());
			}
			Application.EnableVisualStyles();
			Application.SetCompatibleTextRenderingDefault(false);
			try
			{
				Application.Run(new CursForm());
			}
			catch (Exception x)
			{
				MessageBox.Show(x.ToString(), x.GetType().Name, MessageBoxButtons.OK, MessageBoxIcon.Error);
			}
			TrendForm.SaveValues("bnr.xml.tmp");
			System.IO.File.Move("bnr.xml", "bnr.xml.backup");
			System.IO.File.Move("bnr.xml.tmp", "bnr.xml");
			System.IO.File.Delete("bnr.xml.backup");
		}
	}
}
