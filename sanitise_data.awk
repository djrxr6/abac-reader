BEGIN{
	print Title;URL;Date;Month;Year;Decision;Brand;Company;Outcome;Nature of Breach;Medium;Section of Code
	#     1     2   3    NEW   NEW  4        5     6       7       8                9      10
	#Column/field separator
	cs=";"
}
{
	if(NR == 1){
		print $0 \
		      cs"M-Dig" \
		      cs"M-TV" \
		      cs"M-NP"\
		      cs"M-R"\
		      cs"M-C"\
		      cs"M-O"\
		      cs"M-POS"\
		      cs"M-P"\
			cs"C-ai"\
			cs"C-aii"\
			cs"C-aiii"\
			cs"C-aiv"\
			cs"C-bi"\
			cs"C-bii"\
			cs"C-biii"\
			cs"C-biv"\
			cs"C-ci"\
			cs"C-cii"\
			cs"C-ciii"\
			cs"C-civ"\
			cs"C-d"\
			cs"Month"\
			cs"Year"
		}
	else{
		split($3,dateArray," ")
		#print dateArray[2]" "dateArray[3]
		mediumColumns =  ((index($9,"Digital") > 0) ? "1" : " ") \
			cs ((index($9,"Television") > 0) ? "1" : " ") \
			cs ((index($9,"Naming/packaging") > 0) ? "1" : " ")\
			cs ((index($9,"Radio") > 0) ? "1" : " ")\
			cs ((index($9,"Cinema") > 0) ? "1" : " ")\
			cs ((index($9,"Outdoor") > 0) ? "1" : " ")\
			cs ((index($9,"Point of sale") > 0) ? "1" : " ")\
			cs ((index($9,"Print") > 0) ? "1" : " ")
	#	print mediumColumns
		if (index($10,"Part")>0){
			codeSectionColumns = ";;;;;;;;;;;;"
		}
		else{
			codeSectionColumns = ((index($10,"(a)(i)") > 0) ? "1" : " ")\
				cs ((index($10,"(a)(ii)") > 0) ? "1" : " ")\
				cs ((index($10,"(a)(iii)") > 0) ? "1" : " ")\
				cs ((index($10,"(a)(iv)") > 0) ? "1" : " ")\
				cs ((index($10,"(b)(i)") > 0) ? "1" : " ")\
				cs ((index($10,"(b)(ii)") > 0) ? "1" : " ")\
				cs ((index($10,"(b)(iii)") > 0) ? "1" : " ")\
				cs ((index($10,"(b)(iv)") > 0) ? "1" : " ")\
				cs ((index($10,"(c)(i)") > 0) ? "1" : " ")\
				cs ((index($10,"(c)(ii)") > 0) ? "1" : " ")\
				cs ((index($10,"(c)(iii)") > 0) ? "1" : " ")\
				cs ((index($10,"(c)(iv)") > 0) ? "1" : " ")\
				cs ((index($10,"(d)") > 0) ? "1" : "")
		}
		if (substr($0,length($0),1)==";"){
			originalData = substr($0,0,length($0)-1)
		}
		else{
			originalData = $0
		}
		print originalData cs mediumColumns cs codeSectionColumns cs dateArray[2] cs dateArray[3]
	}
}
END{

}
