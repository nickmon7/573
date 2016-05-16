using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Xml;

class Program
{
    private static string sets = @"/dropbox/15-16/573/Data/Documents/devtest/GuidedSumm10_test_topics.xml";

    static void Main(string[] args)
    {
        Preprocess();
    }

    private static void Preprocess()
    {
        // create directory for output
        Directory.CreateDirectory("topics");

        XmlTextReader reader = new XmlTextReader(sets);
        Topic currTopic = null;

        while (reader.Read())
        {
            switch (reader.NodeType)
            {
                case XmlNodeType.Element:
                    switch (reader.Name)
                    {
                        case "topic":
                            currTopic = new Topic();
                            while (reader.MoveToNextAttribute())
                            {
                                switch (reader.Name)
                                {
                                    case "id":
                                        currTopic.id = reader.Value;
                                        break;
                                }
                            }
                            break;
                        case "doc":
                            while (reader.MoveToNextAttribute())
                            {
                                switch (reader.Name)
                                {
                                    case "id":
                                        Document d = new Document(reader.Value);
                                        currTopic.docSet.Add(d);
                                        break;
                                }
                            }
                            break;
                        case "docsetB":
                            reader.Skip();
                            break;
                    }
                    break;
                case XmlNodeType.Text:
                    string headline = Regex.Replace(reader.Value, @"\s+", " ");
                    currTopic.title = headline.Trim();
                    break;
                case XmlNodeType.EndElement:
                    switch (reader.Name)
                    {
                        case "topic":
                            // output as json
                            Console.WriteLine(currTopic.title);
                            List<string> lines = new List<string>();
                            currTopic.Serialize(lines, "");
                            File.WriteAllLines("topics/" + currTopic.id + ".json", lines.ToArray());
                            break;
                    }
                    break;
            }
        }
    }

}


public class Topic
{
    public string id;
    public string title;
    public List<Document> docSet;

    public Topic()
    {
        docSet = new List<Document>();
    }

    public void Serialize(List<string> lines, string tabs)
    {
        lines.Add(tabs + "{");
        tabs += "\t";

        lines.Add(tabs + "\"id\":\"" + id + "\",");
        lines.Add(tabs + "\"title\":\"" + title + "\",");

        lines.Add(tabs + "\"docSet\":[");
        foreach (Document d in docSet)
        {
            d.Serialize(lines, tabs + "\t");
        }
        lines[lines.Count - 1] = lines[lines.Count - 1].TrimEnd(',');
        lines.Add(tabs + "]");

        tabs = tabs.Remove(0, 1);
        lines.Add(tabs + "}");
    }
}


public class Document
{
    public string id;
    public string headline;
    public List<string> sentences;
    public Dictionary<string, int> wordCounts;

    public Document()
    {
        id = "APW19990421.0001";
        sentences = new List<string>();
        wordCounts = new Dictionary<string, int>();
    }

    public Document(string id)
    {
        // id formats:
        // APW19990421.0284
        // XIN_ENG_20041019.0235

        // possible paths:
        // /LDC02T31/apw/1998/19980601_APW_ENG
        // /LDC08T25/data/apw_eng/apw_eng_200410.xml

        // get publication source and year from id
        this.id = id;
        Match m_source = Regex.Match(id, @"^\w{3}");
        string source = m_source.Value;
        Match m_year = Regex.Match(id, @"\d{4}");
        int year = int.Parse(m_year.Value);

        string path = "/corpora/LDC";

        if (year <= 2000)
        {
            Match m_date = Regex.Match(id, @"\d{8}");
            path += "/LDC02T31/" + source.ToLower() + "/" + m_year.Value + "/" + m_date.Value;

            switch (source)
            {
                case "APW":
                    path += "_APW_ENG";
                    break;
                case "NYT":
                    path += "_NYT";
                    break;
                case "XIE":
                    path += "_XIN_ENG";
                    break;
            }
        }
        else
        {
            path += "/LDC08T25/data";

            string name = source.ToLower() + "_" + "eng";
            Match m_date = Regex.Match(id, @"\d{6}");

            path += "/" + name + "/" + name + "_" + m_date.Value + ".xml";
        }

        ReadFile(path);
        GetWordCounts();
    }

    public void ReadFile(string path)
    {
        StreamReader sr = new StreamReader(path);
        
        string line;
        while ((line = sr.ReadLine()) != null)
        {
            if (line.StartsWith("<DOC") && line.Contains(id))
            {
                string text = line;

                while (!line.Contains("</DOC>"))
                {
                    line = sr.ReadLine();
                    text += "\n" + line;
                }

                GetSentences(text);
                break;
            }
        }

        sr.Close();
    }

    private void GetSentences(string doc)
    {
        MatchCollection tags = Regex.Matches(doc, @"(<\w+>|<\/\w+>)");
        sentences = new List<string>();

        int index = 0;
        while (index < tags.Count)
        {
            Match m = tags[index];
            string tag = m.Value;

            if (tag == "</DOC>") { break; }
            if (tag == "<HEADLINE>")
            {
                int start = m.Index + m.Length;
                headline = doc.Substring(start, tags[index + 1].Index - start);
                headline = Regex.Replace(headline, @"\s+", " ").Trim();
                index += 2;
            }
            else if (tag == "<TEXT>")
            {
                while (tags[index].Value != "</TEXT>")
                {
                    index++;
                }

                int start = m.Index + m.Length;
                string text = doc.Substring(start, tags[index].Index - start);
                text = Regex.Replace(text, @"</?P>", " ");
                text = Regex.Replace(text, @"\s+", " ");
                text = Regex.Replace(text, "\"", "\\\"");

                string[] sents = Regex.Split(text.Trim(), @"(?<=[\.!\?])\s+");
                sentences.AddRange(sents);
                break;
            }
            else { index++; }
        }
    }

    private void GetWordCounts()
    {
        wordCounts = new Dictionary<string, int>();

        foreach (string sent in sentences)
        {
            string[] words = sent.Split();

            foreach (string w in words)
            {
                if (wordCounts.ContainsKey(w))
                {
                    wordCounts[w]++;
                }
                else
                {
                    wordCounts.Add(w, 1);
                }
            }
        }
    }

    public void Serialize(List<string> lines, string tabs)
    {
        lines.Add(tabs + "{");
        tabs += "\t";

        lines.Add(tabs + "\"id\":\"" + id + "\",");
        lines.Add(tabs + "\"headline\":\"" + headline + "\",");

        lines.Add(tabs + "\"sentences\":[");
        tabs += "\t";
        foreach (string s in sentences)
        {
            lines.Add(tabs + "\"" + s + "\",");
        }
        lines[lines.Count - 1] = lines[lines.Count - 1].TrimEnd(',');
        tabs = tabs.Remove(0, 1);
        lines.Add(tabs + "],");

        lines.Add(tabs + "\"wordCounts\":{");
        tabs += "\t";
        foreach (KeyValuePair<string, int> kvp in wordCounts)
        {
            lines.Add(tabs + "\"" + kvp.Key + "\":" + kvp.Value + ",");
        }
        lines[lines.Count - 1] = lines[lines.Count - 1].TrimEnd(',');
        tabs = tabs.Remove(0, 1);
        lines.Add(tabs + "}");

        tabs = tabs.Remove(0, 1);
        lines.Add(tabs + "},");
    }


}
